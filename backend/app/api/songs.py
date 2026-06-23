"""
Song ingestion endpoint.

POST /api/song/ingest — accepts a YouTube URL and runs the full
ingestion pipeline (metadata, transcript, vectorization, Neo4j storage).
"""

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from app.database.neo4j import get_neo4j_session
from app.processors import song_processor
from app.schemas.requests import SongIngestRequest
from app.schemas.responses import SongIngestResponse, ErrorResponse
from app.utils.logger import get_logger

logger = get_logger("api.songs")
router = APIRouter(tags=["Songs"])


@router.post(
    "/song/ingest",
    response_model=SongIngestResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Transcript not found"},
        502: {"model": ErrorResponse, "description": "External service failure"},
    },
    summary="Ingest a song from YouTube",
    description=(
        "Accepts a YouTube URL and runs the full ingestion pipeline: "
        "metadata extraction, transcript retrieval (with ElevenLabs fallback), "
        "genre/theme classification, vector embedding, and Neo4j storage."
    ),
)
async def ingest_song(
    request: SongIngestRequest,
    neo4j_session: AsyncSession = Depends(get_neo4j_session),
) -> SongIngestResponse:
    """Ingest a song from YouTube into the Sonus system."""
    logger.info(f"Song ingest request: {request.youtube_url}")

    song = await song_processor.ingest_song(
        youtube_url=str(request.youtube_url),
        neo4j_session=neo4j_session,
    )

    return SongIngestResponse(
        song_id=song.song_id,
        title=song.title,
        artist=song.artist,
        thumbnail=song.thumbnail,
        language=song.language,
        genres=song.genres,
        cultural_themes=song.cultural_themes,
        mood=song.mood,
        era=song.era,
    )
