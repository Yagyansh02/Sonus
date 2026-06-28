"""
Translation processor.

Orchestrates the song translation pipeline:
  1. Retrieve transcript from Neo4j
  2. Perform literary translation via Groq
  3. Store translation in Neo4j
"""

from neo4j import AsyncSession

from app.entities.translation import Translation
from app.services import neo4j_service, translation_service
from app.utils.helpers import generate_id
from app.utils.logger import get_logger
from app.utils.exceptions import SongNotFoundError, TranscriptNotFoundError

logger = get_logger("processors.translation")


async def translate_song(
    song_id: str,
    target_language: str,
    neo4j_session: AsyncSession,
) -> Translation:
    """
    Translate a song's lyrics into the target language.

    Args:
        song_id: ID of the ingested song.
        target_language: Language to translate into (e.g., "Hindi", "Spanish").
        neo4j_session: Active Neo4j async session.

    Returns:
        Translation entity with translated lyrics, notes, and confidence score.

    Raises:
        SongNotFoundError: If the song doesn't exist.
        TranscriptNotFoundError: If the song has no transcript.
    """
    # ── 1. Verify song exists ────────────────────────────────────
    song = await neo4j_service.get_song(neo4j_session, song_id)
    if not song:
        raise SongNotFoundError(song_id)

    # ── 2. Retrieve transcript ───────────────────────────────────
    transcript = await neo4j_service.get_transcript(neo4j_session, song_id)
    if not transcript:
        raise TranscriptNotFoundError(f"No transcript found for song {song_id}")

    # ── 3. Perform literary translation ──────────────────────────
    logger.info(f"Translating song '{song.title}' to {target_language}")
    result = translation_service.translate_lyrics(
        lyrics=transcript.content,
        target_language=target_language,
    )

    # ── 4. Store translation in Neo4j ────────────────────────────
    translation = Translation(
        translation_id=generate_id(),
        song_id=song_id,
        target_language=target_language,
        translated_lyrics=result.translated_lyrics,
        notes=result.translation_notes,
        confidence_score=result.confidence_score,
    )

    await neo4j_service.create_translation(neo4j_session, translation)

    logger.info(
        f"Translation stored: {translation.translation_id} "
        f"({target_language}, confidence={translation.confidence_score:.2f})"
    )
    return translation
