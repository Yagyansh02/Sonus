"""
Custom exception hierarchy for the Sonus backend.

Each exception carries a machine-readable ``error_code`` and
an HTTP ``status_code`` so the global handler can translate it
into a consistent API error response.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


# ── Base Exception ───────────────────────────────────────────────

class SonusException(Exception):
    """Base exception for all Sonus application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        error_code: str = "SONUS_ERROR",
        status_code: int = 500,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


# ── Resource Not Found ───────────────────────────────────────────

class SongNotFoundError(SonusException):
    def __init__(self, song_id: str):
        super().__init__(
            message=f"Song not found: {song_id}",
            error_code="SONG_NOT_FOUND",
            status_code=404,
        )


class TranscriptNotFoundError(SonusException):
    def __init__(self, detail: str = "Transcript unavailable from all sources"):
        super().__init__(
            message=detail,
            error_code="TRANSCRIPT_NOT_FOUND",
            status_code=404,
        )


class SessionNotFoundError(SonusException):
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            error_code="SESSION_NOT_FOUND",
            status_code=404,
        )


# ── Processing Errors ───────────────────────────────────────────

class TranslationError(SonusException):
    def __init__(self, detail: str = "Translation processing failed"):
        super().__init__(
            message=detail,
            error_code="TRANSLATION_ERROR",
            status_code=500,
        )


class RAGProcessingError(SonusException):
    def __init__(self, detail: str = "RAG pipeline processing failed"):
        super().__init__(
            message=detail,
            error_code="RAG_PROCESSING_ERROR",
            status_code=500,
        )


# ── External Service Errors ──────────────────────────────────────

class ExternalServiceError(SonusException):
    def __init__(self, service: str, detail: str = ""):
        super().__init__(
            message=f"External service error [{service}]: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
        )


class YouTubeExtractionError(ExternalServiceError):
    def __init__(self, detail: str = "YouTube data extraction failed"):
        super().__init__(service="YouTube", detail=detail)


class ElevenLabsError(ExternalServiceError):
    def __init__(self, detail: str = "ElevenLabs API request failed"):
        super().__init__(service="ElevenLabs", detail=detail)


class Neo4jConnectionError(ExternalServiceError):
    def __init__(self, detail: str = "Neo4j database connection failed"):
        super().__init__(service="Neo4j", detail=detail)


# ── Validation Errors ────────────────────────────────────────────

class InvalidYouTubeURLError(SonusException):
    def __init__(self, url: str):
        super().__init__(
            message=f"Invalid YouTube URL: {url}",
            error_code="INVALID_YOUTUBE_URL",
            status_code=400,
        )


# ── Global Exception Handler ────────────────────────────────────

async def sonus_exception_handler(request: Request, exc: SonusException) -> JSONResponse:
    """FastAPI exception handler that converts SonusExceptions into JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
        },
    )
