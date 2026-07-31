"""
Lyrics structure analyser.

Uses Groq with ``llm.with_structured_output(SongStructure)`` to segment
raw, unstructured lyrics into labelled musical sections (Verse 1, Chorus,
Bridge, Outro, etc.) before chunking.

Pipeline role:
    transcript -> [lyrics_structurizer] -> SongStructure -> [vector_service]
    -> per-section RecursiveCharacterTextSplitter -> LyricChunk list

Design principles:
  - Single responsibility: ONLY does section tagging, no chunking.
  - Non-fatal: always returns *something* (falls back to a single
    "Full Song" section) so ingestion never aborts due to a structuring
    failure.
  - Same retry pattern as song_processor._call_metadata_llm (tenacity,
    3 attempts, exponential back-off).
  - Prompt lives in constants.py alongside the other prompt templates.
"""

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.constants import LYRICS_STRUCTURE_PROMPT
from app.schemas.llm_outputs import SongSection, SongStructure
from app.services import groq_service
from app.utils.logger import get_logger

logger = get_logger("services.lyrics_structurizer")

# Minimum transcript length to bother calling Groq.
# Very short strings (intros, instrumentals) are returned as-is.
_MIN_LYRICS_LEN = 100


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_structure_llm(lyrics: str) -> SongStructure:
    """
    Inner Groq call wrapped by tenacity for automatic retry.

    Separated so the retry decorator wraps only the network call,
    not the surrounding fallback logic.
    """
    llm = groq_service.get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(SongStructure)

    prompt = LYRICS_STRUCTURE_PROMPT.format(lyrics=lyrics)

    return structured_llm.invoke([{"role": "user", "content": prompt}])


def tag_song_structure(lyrics: str) -> list[SongSection]:
    """
    Analyse raw lyrics and return an ordered list of labelled musical sections.

    Each ``SongSection`` carries:
        section_type  (str)  -- e.g. "Verse 1", "Chorus", "Bridge"
        lyrics        (str)  -- verbatim text of that section

    Guarantees:
        - Always returns a non-empty list (never raises).
        - On any failure (Groq error, short transcript, parse failure),
          falls back to a single ``SongSection(section_type="Full Song",
          lyrics=<original text>)``, preserving the full ingestion pipeline.

    Args:
        lyrics: Raw, unstructured lyrics/transcript text.

    Returns:
        Ordered list of SongSection objects covering the entire lyrics.
    """
    if not lyrics or not lyrics.strip():
        logger.warning("Empty lyrics passed to structurizer -- returning empty list")
        return []

    # Skip LLM call for very short content (not worth the API cost / latency)
    if len(lyrics.strip()) < _MIN_LYRICS_LEN:
        logger.info(
            f"Lyrics too short ({len(lyrics)} chars) for structure analysis -- "
            "treating as single 'Full Song' section"
        )
        return [SongSection(section_type="Full Song", lyrics=lyrics)]

    logger.info(f"Analysing song structure via Groq ({len(lyrics)} chars)...")

    try:
        result: SongStructure = _call_structure_llm(lyrics)

        if not result.sections:
            raise ValueError("Groq returned an empty sections list")

        logger.info(
            f"Structure analysis complete: {len(result.sections)} sections -- "
            + ", ".join(s.section_type for s in result.sections)
        )
        return result.sections

    except Exception as e:
        # Non-fatal fallback: log the error and continue ingestion as a
        # single monolithic chunk. This matches the spirit of the transcript
        # fallback in transcript_processor.
        logger.warning(
            f"Lyrics structure analysis failed after retries ({e}). "
            "Falling back to single 'Full Song' section -- ingestion continues."
        )
        return [SongSection(section_type="Full Song", lyrics=lyrics)]
