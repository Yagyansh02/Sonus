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
