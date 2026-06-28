"""
RAG (Retrieval-Augmented Generation) endpoint.

POST /api/rag/ask — ask a question about a song using the
conversational cultural interpretation pipeline.
"""

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from app.database.neo4j import get_neo4j_session
from app.processors import rag_processor
from app.schemas.rag import RAGAskRequest, RAGAskResponse
from app.schemas.error import ErrorResponse
from app.utils.logger import get_logger

logger = get_logger("api.rag")
router = APIRouter(prefix="/rag", tags=["RAG - Cultural Interpretation"])


@router.post(
    "/ask",
    response_model=RAGAskResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Song not found"},
        500: {"model": ErrorResponse, "description": "RAG processing error"},
    },
    summary="Ask about a song",
    description=(
        "Ask a question about a song's lyrics, meaning, cultural references, "
        "metaphors, or themes. Uses a conversational RAG pipeline with "
        "ethnomusicologist-level interpretation. Session history is maintained "
        "for follow-up questions."
    ),
)
async def ask_about_song(
    request: RAGAskRequest,
    neo4j_session: AsyncSession = Depends(get_neo4j_session),
) -> RAGAskResponse:
    """
    Cultural interpretation endpoint.

    The assistant explains slang, metaphors, cultural references,
    emotional context, and artist intent using retrieved lyric chunks.
    """
    logger.info(
        f"RAG ask: song={request.song_id} session={request.session_id} "
        f"q='{request.question[:80]}...'"
    )

    result = await rag_processor.ask_question(
        song_id=request.song_id,
        session_id=request.session_id,
        question=request.question,
        neo4j_session=neo4j_session,
    )

    return RAGAskResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=result["session_id"],
        song_id=result["song_id"],
    )
