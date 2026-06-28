"""
Song ingestion processor.

Orchestrates the full song ingestion pipeline:
  1. Check if song already exists (by URL)
  2. Fetch metadata from YouTube
  3. Retrieve transcript (with fallback)
  4. Extract genre & cultural themes via LLM (structured output, 3 retries)
  5. Chunk transcript and embed into Neo4j Chunk nodes
  6. Store Song, Transcript in Neo4j

Structured output (llm.with_structured_output) is used so the Groq API
enforces the SongMetadata schema — no JSON parsing, no fence-stripping.

Tenacity retries the metadata extraction up to 3 times.  If all attempts
fail the ingestion is aborted (exception raised) and no data is written.
"""

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from neo4j import AsyncSession

from app.config.constants import METADATA_EXTRACTION_PROMPT
from app.entities.song import Song
from app.entities.transcript import Transcript
from app.processors import transcript_processor
from app.schemas.llm_outputs import SongMetadata
from app.services import groq_service, neo4j_service, vector_service, youtube_service
from app.utils.helpers import generate_id, truncate_text
from app.utils.exceptions import ExternalServiceError
from app.utils.logger import get_logger

logger = get_logger("processors.song")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_metadata_llm(title: str, artist: str, lyrics_excerpt: str) -> SongMetadata:
    """
    Inner LLM call wrapped by tenacity for automatic retry.

    Separated so the retry decorator wraps only the network call,
    not the surrounding ingestion logic.
    """
    llm = groq_service.get_llm(temperature=0.1)
    structured_llm = llm.with_structured_output(SongMetadata)

    prompt = METADATA_EXTRACTION_PROMPT.format(
        title=title,
        artist=artist,
        lyrics_excerpt=lyrics_excerpt,
    )

    return structured_llm.invoke([
        {"role": "user", "content": prompt},
    ])


def _extract_metadata_via_llm(title: str, artist: str, lyrics: str) -> SongMetadata:
    """
    Use the Groq LLM to extract genre, cultural themes, language, mood, and era.

    Uses ``llm.with_structured_output(SongMetadata)`` so the Groq API
    enforces the exact schema — no manual JSON parsing.

    Retries up to 3 times (exponential back-off) via Tenacity.

    Args:
        title:   Song title for context.
        artist:  Artist name for context.
        lyrics:  Full lyrics text (will be truncated to 1500 chars).

    Returns:
        A validated SongMetadata instance.

    Raises:
        ExternalServiceError: If all 3 retry attempts fail.
            The caller MUST NOT write any data to the database in this case.
    """
    logger.info(f"Extracting metadata via LLM for: '{title}'")

    try:
        result: SongMetadata = _call_metadata_llm(
            title=title,
            artist=artist,
            lyrics_excerpt=truncate_text(lyrics, 1500),
        )
        logger.info(
            f"Metadata extracted: language={result.language} "
            f"genres={result.genres} themes={result.cultural_themes}"
        )
        return result

    except Exception as e:
        # All 3 retries exhausted — abort with a clear error.
        # We deliberately do NOT return a default here to prevent
        # corrupted / default data from being written to Neo4j.
        logger.error(
            f"LLM metadata extraction failed after 3 attempts for '{title}': {e}. "
            "Aborting ingestion to prevent corrupted data in the database."
        )
        raise ExternalServiceError(
            service="Groq",
            detail=(
                f"Metadata extraction failed after 3 retries for song '{title}'. "
                f"Root cause: {e}"
            ),
        )


async def ingest_song(youtube_url: str, neo4j_session: AsyncSession) -> Song:
    """
    Full song ingestion pipeline.

    If the song has already been ingested (same URL), returns the
    existing record without re-processing.

    Args:
        youtube_url:   Full YouTube video URL.
        neo4j_session: Active Neo4j async session.

    Returns:
        The Song entity (new or existing).

    Raises:
        TranscriptNotFoundError: If transcript cannot be obtained from any source.
        ExternalServiceError: If LLM metadata extraction fails after all retries.
    """
    url_str = str(youtube_url)

    # ── 1. Check for existing song ───────────────────────────────
    existing = await neo4j_service.get_song_by_url(neo4j_session, url_str)
    if existing:
        logger.info(f"Song already ingested: {existing.song_id} ({existing.title})")
        return existing

    # ── 2. Fetch YouTube metadata ────────────────────────────────
    song_id = generate_id()
    metadata = youtube_service.fetch_video_metadata(url_str)

    # ── 3. Retrieve transcript (with fallback) ───────────────────
    transcript_content, transcript_source = transcript_processor.get_transcript(
        url_str, song_id
    )

    # ── 4. Extract genre & cultural themes via LLM ───────────────
    # Raises ExternalServiceError on failure — no data is written to DB.
    enrichment: SongMetadata = _extract_metadata_via_llm(
        title=metadata["title"],
        artist=metadata["artist"],
        lyrics=transcript_content,
    )

    # ── 5. Build the Song entity ─────────────────────────────────
    song = Song(
        song_id=song_id,
        title=metadata["title"],
        artist=metadata["artist"],
        youtube_url=url_str,
        thumbnail=metadata["thumbnail"],
        language=enrichment.language,
        genres=enrichment.genres,
        cultural_themes=enrichment.cultural_themes,
        mood=enrichment.mood,
        era=enrichment.era,
    )

    # ── 6. Store in Neo4j ────────────────────────────────────────
    await neo4j_service.create_song(neo4j_session, song)

    transcript = Transcript(
        transcript_id=generate_id(),
        song_id=song_id,
        content=transcript_content,
        source=transcript_source,
    )
    await neo4j_service.create_transcript(neo4j_session, transcript)

    # ── 7. Chunk & embed transcript into Neo4j Chunk nodes ───────
    # Guard: skip if chunks already exist (idempotent re-ingestion)
    has_chunks = await neo4j_service.song_has_chunks(neo4j_session, song_id)
    if not has_chunks:
        chunks = vector_service.chunk_and_embed(
            song_id=song_id,
            transcript_content=transcript_content,
            metadata={
                "title": song.title,
                "artist": song.artist,
                "source": transcript_source,
            },
        )
        await neo4j_service.store_chunks(neo4j_session, song_id, chunks)
    else:
        logger.info(f"Chunks already exist for song {song_id}, skipping re-embedding")

    logger.info(
        f"Song ingested: {song_id} | '{song.title}' by {song.artist} | "
        f"genres={song.genres} | themes={song.cultural_themes}"
    )
    return song
