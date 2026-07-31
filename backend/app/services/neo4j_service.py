"""
Neo4j data access service.

Async CRUD methods wrapping the Cypher queries defined in database/queries.py.
Each method accepts an AsyncSession and returns domain entities.
"""

from neo4j import AsyncSession

from app.database import queries as Q
from app.entities.song import Song
from app.entities.transcript import Transcript
from app.entities.translation import Translation
from app.entities.session import Session
from app.schemas.chunk import LyricChunk
from app.utils.logger import get_logger

logger = get_logger("services.neo4j")


# ── Song ─────────────────────────────────────────────────────────

async def create_song(session: AsyncSession, song: Song) -> Song:
    """Create or update a Song node and link to Artist, Genres, and CulturalThemes."""

    # Create the Song node
    await session.run(
        Q.CREATE_SONG,
        song_id=song.song_id,
        title=song.title,
        youtube_url=song.youtube_url,
        thumbnail=song.thumbnail,
        language=song.language,
        mood=song.mood,
        era=song.era,
    )

    # Create Artist and relationship
    if song.artist and song.artist != "Unknown Artist":
        await session.run(
            Q.CREATE_ARTIST_AND_LINK,
            artist_name=song.artist,
            song_id=song.song_id,
        )

    # Link genres
    for genre in song.genres:
        await session.run(
            Q.LINK_SONG_TO_GENRE,
            genre_name=genre,
            song_id=song.song_id,
        )

    # Link cultural themes
    for theme in song.cultural_themes:
        await session.run(
            Q.LINK_SONG_TO_CULTURAL_THEME,
            theme_name=theme,
            song_id=song.song_id,
        )

    logger.info(f"Song created/updated in Neo4j: {song.song_id}")
    return song


async def get_song(session: AsyncSession, song_id: str) -> Song | None:
    """Retrieve a Song by its ID, including related Artist, Genres, and CulturalThemes."""
    result = await session.run(Q.GET_SONG_BY_ID, song_id=song_id)
    record = await result.single()

    if not record:
        return None

    s = record["s"]
    return Song(
        song_id=s["song_id"],
        title=s.get("title", "Unknown Track"),
        artist=record.get("artist", "Unknown Artist") or "Unknown Artist",
        youtube_url=s.get("youtube_url", ""),
        thumbnail=s.get("thumbnail", ""),
        language=s.get("language", "Unknown"),
        genres=record.get("genres", []),
        cultural_themes=record.get("cultural_themes", []),
        mood=s.get("mood", ""),
        era=s.get("era", ""),
    )


async def get_song_by_url(session: AsyncSession, youtube_url: str) -> Song | None:
    """Retrieve a Song by its YouTube URL."""
    result = await session.run(Q.GET_SONG_BY_URL, youtube_url=youtube_url)
    record = await result.single()

    if not record:
        return None

    s = record["s"]
    return Song(
        song_id=s["song_id"],
        title=s.get("title", "Unknown Track"),
        artist=record.get("artist", "Unknown Artist") or "Unknown Artist",
        youtube_url=s.get("youtube_url", ""),
        thumbnail=s.get("thumbnail", ""),
        language=s.get("language", "Unknown"),
        genres=record.get("genres", []),
        cultural_themes=record.get("cultural_themes", []),
        mood=s.get("mood", ""),
        era=s.get("era", ""),
    )


# ── Transcript ───────────────────────────────────────────────────

async def create_transcript(
    session: AsyncSession,
    transcript: Transcript,
) -> Transcript:
    """Create a Transcript node and link it to its Song."""
    await session.run(
        Q.CREATE_TRANSCRIPT,
        transcript_id=transcript.transcript_id,
        song_id=transcript.song_id,
        content=transcript.content,
        source=transcript.source,
    )
    logger.info(f"Transcript created: {transcript.transcript_id} (source={transcript.source})")
    return transcript


async def get_transcript(session: AsyncSession, song_id: str) -> Transcript | None:
    """Retrieve the transcript for a song."""
    result = await session.run(Q.GET_TRANSCRIPT_BY_SONG_ID, song_id=song_id)
    record = await result.single()

    if not record:
        return None

    t = record["t"]
    return Transcript(
        transcript_id=t["transcript_id"],
        song_id=song_id,
        content=t["content"],
        source=t.get("source", "youtube"),
    )


# ── Translation ──────────────────────────────────────────────────

async def create_translation(
    session: AsyncSession,
    translation: Translation,
) -> Translation:
    """Create a Translation node and link it to its Song."""
    await session.run(
        Q.CREATE_TRANSLATION,
        translation_id=translation.translation_id,
        song_id=translation.song_id,
        target_language=translation.target_language,
        translated_lyrics=translation.translated_lyrics,
        notes=translation.notes,
        confidence_score=translation.confidence_score,
    )
    logger.info(f"Translation created: {translation.translation_id}")
    return translation


async def get_translations(session: AsyncSession, song_id: str) -> list[Translation]:
    """Retrieve all translations for a song."""
    result = await session.run(Q.GET_TRANSLATIONS_BY_SONG_ID, song_id=song_id)
    records = [record async for record in result]

    translations = []
    for record in records:
        tr = record["tr"]
        translations.append(Translation(
            translation_id=tr["translation_id"],
            song_id=song_id,
            target_language=tr["target_language"],
            translated_lyrics=tr["translated_lyrics"],
            notes=tr.get("notes", ""),
            confidence_score=tr.get("confidence_score", 0.0),
        ))

    return translations


# ── Session ──────────────────────────────────────────────────────

async def create_or_get_session(session: AsyncSession, session_id: str) -> Session:
    """Create a Session node if it doesn't exist, or return the existing one."""
    result = await session.run(Q.CREATE_SESSION, session_id=session_id)
    record = await result.single()
    sess = record["sess"]

    return Session(
        session_id=sess["session_id"],
        created_at=str(sess.get("created_at", "")),
    )


async def link_session_to_song(
    session: AsyncSession,
    session_id: str,
    song_id: str,
) -> None:
    """Create the (Session)-[:ASKED]->(Song) relationship."""
    await session.run(
        Q.LINK_SESSION_TO_SONG,
        session_id=session_id,
        song_id=song_id,
    )
    logger.info(f"Linked session {session_id} -> song {song_id}")


# ── Chunk (Vector Embeddings) ─────────────────────────────────────

async def store_chunks(
    session: AsyncSession,
    song_id: str,
    chunks: list[LyricChunk],
) -> None:
    """
    Bulk upsert Chunk nodes and link them to their Song.

    Args:
        session:  Active Neo4j async session.
        song_id:  The owning song's ID.
        chunks:   List of LyricChunk DTOs produced by vector_service.chunk_and_embed().
                  Each chunk carries a section_type from the structural chunking step.
    """
    for chunk in chunks:
        await session.run(
            Q.UPSERT_CHUNK,
            chunk_id=chunk.chunk_id,
            song_id=song_id,
            content=chunk.content,
            embedding=chunk.embedding,
            chunk_index=chunk.chunk_index,
            section_type=chunk.section_type,
        )
    logger.info(f"Stored {len(chunks)} chunks for song {song_id}")


async def search_vector_chunks(
    session: AsyncSession,
    song_id: str,
    query_embedding: list[float],
    k: int = 4,
) -> list[dict]:
    """
    Retrieve the k most semantically similar lyric chunks for a specific song.

    Uses exact KNN via graph traversal and real-time cosine similarity -- NOT
    global ANN post-filtering -- so recall is perfect regardless of k.

    Args:
        session:         Active Neo4j async session.
        song_id:         Restrict search to this song's chunks only.
        query_embedding: Embedded question vector (384 dims).
        k:               Number of top chunks to return.

    Returns:
        List of dicts with keys: content, chunk_index, section_type, score.
    """
    result = await session.run(
        Q.SEARCH_SIMILAR_CHUNKS,
        song_id=song_id,
        query_embedding=query_embedding,
        k=k,
    )
    records = [record async for record in result]
    return [
        {
            "content": record["content"],
            "chunk_index": record["chunk_index"],
            "section_type": record.get("section_type", "Unknown"),
            "score": record["score"],
        }
        for record in records
    ]


async def search_similar_chunks(
    session: AsyncSession,
    song_id: str,
    query_embedding: list[float],
    k: int = 4,
) -> list[dict]:
    """
    Backward-compatible alias for search_vector_chunks().

    Existing callers (e.g. tests, notebooks) will continue to work without
    any changes. New code should call search_vector_chunks() directly.
    """
    return await search_vector_chunks(session, song_id, query_embedding, k)


async def search_bm25_chunks(
    session: AsyncSession,
    song_id: str,
    query_text: str,
    k: int = 8,
) -> list[dict]:
    """
    Retrieve lyric chunks for a song using BM25 full-text (keyword) search.

    The Neo4j full-text index is global, but results are filtered to the
    specific song via ``WHERE node.song_id = $song_id`` before the LIMIT
    is applied.  No results from other songs can appear.

    Args:
        session:    Active Neo4j async session.
        song_id:    Restrict results to this song's chunks only.
        query_text: Raw query string for full-text matching.
        k:          Maximum number of chunks to return.

    Returns:
        List of dicts with keys: content, chunk_index, section_type, score.
    """
    result = await session.run(
        Q.SEARCH_BM25_CHUNKS,
        song_id=song_id,
        query_text=query_text,
        k=k,
    )
    records = [record async for record in result]
    return [
        {
            "content": record["content"],
            "chunk_index": record["chunk_index"],
            "section_type": record.get("section_type", "Unknown"),
            "score": record["score"],
        }
        for record in records
    ]


async def song_has_chunks(session: AsyncSession, song_id: str) -> bool:
    """Return True if the song already has Chunk nodes stored in Neo4j."""
    result = await session.run(Q.SONG_HAS_CHUNKS, song_id=song_id)
    record = await result.single()
    return bool(record and record["chunk_count"] > 0)


# ── Setup ────────────────────────────────────────────────────────

async def setup_constraints(session: AsyncSession) -> None:
    """Run all uniqueness constraints. Safe to call repeatedly."""
    for query in Q.SETUP_CONSTRAINTS:
        try:
            await session.run(query)
        except Exception as e:
            # Some Neo4j editions don't support all constraint types
            logger.warning(f"Constraint setup note: {e}")
    logger.info("Neo4j constraints initialized")


async def setup_vector_index(session: AsyncSession) -> None:
    """Create the Chunk embedding vector index. Safe to call repeatedly (IF NOT EXISTS)."""
    try:
        await session.run(Q.SETUP_VECTOR_INDEX)
        logger.info("Neo4j vector index initialized (chunk_embedding_index)")
    except Exception as e:
        logger.warning(f"Vector index setup note: {e}")


async def setup_bm25_index(session: AsyncSession) -> None:
    """
    Create the Chunk full-text (BM25) index. Safe to call repeatedly (IF NOT EXISTS).

    The index covers Chunk.content and is used by search_bm25_chunks().
    Results are always scoped to a specific song via WHERE in the query.
    """
    try:
        await session.run(Q.SETUP_BM25_INDEX)
        logger.info("Neo4j BM25 full-text index initialized (chunk_content_bm25_index)")
    except Exception as e:
        logger.warning(f"BM25 index setup note: {e}")
