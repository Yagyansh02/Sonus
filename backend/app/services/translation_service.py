"""
Translation service.

Uses the Groq LLM to perform literary localization of song lyrics,
preserving poetic meaning, metaphors, and cultural nuance.

Structured output (llm.with_structured_output) is used so the Groq API
enforces the response schema at the model level — no JSON parsing,
no fence-stripping, no runtime KeyErrors.

Tenacity retries the call up to 3 times with exponential back-off
before re-raising as a TranslationError.
"""

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.constants import TRANSLATION_SYSTEM_PROMPT
from app.schemas.llm_outputs import TranslationResult
from app.services.groq_service import get_llm
from app.utils.logger import get_logger
from app.utils.exceptions import TranslationError

logger = get_logger("services.translation")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_translation_llm(
    lyrics: str,
    target_language: str,
    temperature: float,
) -> TranslationResult:
    """
    Inner call that is retried by tenacity.

    Separated so the retry decorator wraps only the LLM invocation,
    not the surrounding business logic.
    """
    llm = get_llm(temperature=temperature)
    structured_llm = llm.with_structured_output(TranslationResult)

    system_prompt = TRANSLATION_SYSTEM_PROMPT.format(target_language=target_language)

    return structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Translate the following lyrics:\n\n{lyrics}"},
    ])


def translate_lyrics(
    lyrics: str,
    target_language: str,
    temperature: float = 0.4,
) -> TranslationResult:
    """
    Translate song lyrics into the target language using literary localization.

    The translation preserves poetic meaning, emotional impact, metaphors,
    symbolism, cultural references, and artistic intent.

    Uses ``llm.with_structured_output(TranslationResult)`` — the Groq API
    guarantees the exact schema, eliminating all manual JSON parsing.

    Retries up to 3 times (exponential back-off) via Tenacity before raising.

    Args:
        lyrics: Original song lyrics text.
        target_language: The language to translate into.
        temperature: LLM temperature for creative translation.

    Returns:
        A validated TranslationResult with translated_lyrics, translation_notes,
        and confidence_score fields.

    Raises:
        TranslationError: If all 3 retry attempts fail.
    """
    logger.info(f"Translating lyrics to {target_language} ({len(lyrics)} chars)")

    try:
        result: TranslationResult = _call_translation_llm(lyrics, target_language, temperature)
        logger.info(
            f"Translation complete: confidence={result.confidence_score:.2f}"
        )
        return result

    except Exception as e:
        logger.error(f"Translation failed after 3 attempts: {e}")
        raise TranslationError(detail=str(e))
