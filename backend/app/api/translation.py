"""
Translation endpoints.

POST /api/translate          — translate a song's lyrics
GET  /api/song/{song_id}/translations — list all translations for a song
"""

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from app.database.neo4j import get_neo4j_session
from app.processors import song_processor, translation_processor
from app.schemas.requests import TranslateRequest
from app.schemas.responses import (
    ErrorResponse,
    TranslationListResponse,
    TranslationResponse,
)
from app.services import neo4j_service
from app.utils.exceptions import SongNotFoundError
from app.utils.logger import get_logger

logger = get_logger("api.translation")
router = APIRouter(tags=["Translation"])


@router.post(
    "/translate",
    response_model=TranslationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Song or transcript not found"},
    },
    summary="Translate song lyrics",
    description=(
        "Translate a song's lyrics into the specified target language. "
        "Uses literary localization to preserve poetic meaning, metaphors, "
        "and cultural references. Provide either song_id or youtube_url."
    ),
)
async def translate_song(
    request: TranslateRequest,
    neo4j_session: AsyncSession = Depends(get_neo4j_session),
) -> TranslationResponse:
    """Translate a song's lyrics into the target language."""
    song_id = request.song_id

    # If youtube_url is provided instead of song_id, ingest first
    if not song_id and request.youtube_url:
        logger.info(f"Auto-ingesting song from URL before translation: {request.youtube_url}")
        song = await song_processor.ingest_song(
            youtube_url=str(request.youtube_url),
            neo4j_session=neo4j_session,
        )
        song_id = song.song_id
    elif not song_id:
        from app.utils.exceptions import SonusException
        raise SonusException(
            message="Either song_id or youtube_url must be provided",
            error_code="INVALID_REQUEST",
            status_code=400,
        )

    translation = await translation_processor.translate_song(
        song_id=song_id,
        target_language=request.target_language,
        neo4j_session=neo4j_session,
    )

    return TranslationResponse(
        translation_id=translation.translation_id,
        song_id=translation.song_id,
        target_language=translation.target_language,
        translated_lyrics=translation.translated_lyrics,
        translation_notes=translation.notes,
        confidence_score=translation.confidence_score,
    )


@router.get(
    "/song/{song_id}/translations",
    response_model=TranslationListResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Song not found"},
    },
    summary="List all translations for a song",
    description="Retrieve all available translations for an ingested song.",
)
async def list_translations(
    song_id: str,
    neo4j_session: AsyncSession = Depends(get_neo4j_session),
) -> TranslationListResponse:
    """List all translations for a given song."""
    logger.info(f"Listing translations for song_id={song_id}")

    # Verify song exists
    song = await neo4j_service.get_song(neo4j_session, song_id)
    if not song:
        raise SongNotFoundError(song_id)

    translations = await neo4j_service.get_translations(neo4j_session, song_id)

    return TranslationListResponse(
        song_id=song_id,
        translations=[
            TranslationResponse(
                translation_id=t.translation_id,
                song_id=t.song_id,
                target_language=t.target_language,
                translated_lyrics=t.translated_lyrics,
                translation_notes=t.notes,
                confidence_score=t.confidence_score,
            )
            for t in translations
        ],
        count=len(translations),
    )
