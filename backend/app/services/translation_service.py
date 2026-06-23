"""
Translation service.

Uses the Groq LLM to perform literary localization of song lyrics,
preserving poetic meaning, metaphors, and cultural nuance.
"""

import json

from app.config.constants import TRANSLATION_SYSTEM_PROMPT
from app.services.groq_service import get_llm
from app.utils.logger import get_logger
from app.utils.exceptions import TranslationError

logger = get_logger("services.translation")


def translate_lyrics(
    lyrics: str,
    target_language: str,
    temperature: float = 0.4,
) -> dict:
    """
    Translate song lyrics into the target language using literary localization.

    The translation preserves poetic meaning, emotional impact, metaphors,
    symbolism, cultural references, and artistic intent.

    Args:
        lyrics: Original song lyrics text.
        target_language: The language to translate into.
        temperature: LLM temperature for creative translation.

    Returns:
        dict with keys: translated_lyrics, translation_notes, confidence_score

    Raises:
        TranslationError: If the LLM response cannot be parsed.
    """
    logger.info(f"Translating lyrics to {target_language} ({len(lyrics)} chars)")

    llm = get_llm(temperature=temperature)

    # Format the translation prompt with the target language
    system_prompt = TRANSLATION_SYSTEM_PROMPT.format(target_language=target_language)

    try:
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate the following lyrics:\n\n{lyrics}"},
        ])

        # Parse the JSON response
        content = response.content.strip()

        # Handle potential markdown code fences in the response
        if content.startswith("```"):
            content = content.split("\n", 1)[1]  # remove first line
            content = content.rsplit("```", 1)[0]  # remove last fence
            content = content.strip()

        result = json.loads(content, strict=False)

        # Validate required fields
        if "translated_lyrics" not in result:
            raise TranslationError("LLM response missing 'translated_lyrics' field")

        translation = {
            "translated_lyrics": result["translated_lyrics"],
            "translation_notes": result.get("translation_notes", ""),
            "confidence_score": float(result.get("confidence_score", 0.8)),
        }

        logger.info(
            f"Translation complete: confidence={translation['confidence_score']:.2f}"
        )
        return translation

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM translation response: {e}")
        raise TranslationError(f"Could not parse translation response: {e}")
    except TranslationError:
        raise
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise TranslationError(detail=str(e))
