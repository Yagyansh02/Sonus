"""
Song ingestion processor.

Orchestrates the full song ingestion pipeline:
  1. Check if song already exists (by URL)
  2. Fetch metadata from YouTube
  3. Retrieve transcript (with fallback)
  4. Extract genre & cultural themes via LLM
  5. Chunk transcript and embed into Neo4j Chunk nodes
  6. Store Song, Transcript in Neo4j
"""

import json

from neo4j import AsyncSession

from app.config.constants import METADATA_EXTRACTION_PROMPT
from app.entities.song import Song
from app.entities.transcript import Transcript
from app.processors import transcript_processor
from app.services import groq_service, neo4j_service, vector_service, youtube_service
from app.utils.helpers import generate_id, truncate_text
from app.utils.logger import get_logger

logger = get_logger("processors.song")


def _extract_metadata_via_llm(title: str, artist: str, lyrics: str) -> dict:
    """
    Use the Groq LLM to extract genre, cultural themes, language, mood, and era.

    Returns a dict with keys: genres, cultural_themes, language, mood, era.
    Falls back to sensible defaults on failure.
    """
    logger.info(f"Extracting metadata via LLM for: '{title}'")
    llm = groq_service.get_llm(temperature=0.1)

    prompt = METADATA_EXTRACTION_PROMPT.format(
        title=title,
        artist=artist,
        lyrics_excerpt=truncate_text(lyrics, 1500),
    )

    try:
        response = llm.invoke([
            {"role": "user", "content": prompt},
        ])

        content = response.content.strip()

        # Handle markdown code fences
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
            content = content.strip()

        result = json.loads(content)
        return {
            "genres": result.get("genres", []),
            "cultural_themes": result.get("cultural_themes", []),
            "language": result.get("language", "Unknown"),
            "mood": result.get("mood", ""),
            "era": result.get("era", ""),
        }
    except Exception as e:
        logger.warning(f"LLM metadata extraction failed: {e}. Using defaults.")
        return {
            "genres": [],
            "cultural_themes": [],
            "language": "Unknown",
            "mood": "",
            "era": "",
        }


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
    enrichment = _extract_metadata_via_llm(
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
        language=enrichment["language"],
        genres=enrichment["genres"],
        cultural_themes=enrichment["cultural_themes"],
        mood=enrichment["mood"],
        era=enrichment["era"],
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
