"""
Transcript retrieval endpoint.

GET /api/song/{song_id}/transcript — returns the stored transcript for a song.
"""

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from app.database.neo4j import get_neo4j_session
from app.schemas.responses import TranscriptResponse, ErrorResponse
from app.services import neo4j_service
from app.utils.exceptions import SongNotFoundError, TranscriptNotFoundError
from app.utils.logger import get_logger

logger = get_logger("api.transcript")
router = APIRouter(tags=["Transcript"])


@router.get(
    "/song/{song_id}/transcript",
    response_model=TranscriptResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Song or transcript not found"},
    },
    summary="Get song transcript",
    description="Retrieve the stored transcript for an ingested song.",
)
async def get_transcript(
    song_id: str,
    neo4j_session: AsyncSession = Depends(get_neo4j_session),
) -> TranscriptResponse:
    """Retrieve the transcript for a given song."""
    logger.info(f"Transcript request for song_id={song_id}")

    # Verify song exists
    song = await neo4j_service.get_song(neo4j_session, song_id)
    if not song:
        raise SongNotFoundError(song_id)

    # Get transcript
    transcript = await neo4j_service.get_transcript(neo4j_session, song_id)
    if not transcript:
        raise TranscriptNotFoundError(f"No transcript found for song {song_id}")

    return TranscriptResponse(
        transcript_id=transcript.transcript_id,
        song_id=transcript.song_id,
        content=transcript.content,
        source=transcript.source,
    )
