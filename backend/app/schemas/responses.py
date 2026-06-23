"""
Pydantic response models for API serialization.

Every outgoing response is serialized through these schemas
for consistent API contracts.
"""

from pydantic import BaseModel, Field


# ── Health ───────────────────────────────────────────────────────

class ServiceStatus(BaseModel):
    neo4j: str = "unknown"
    vector_store: str = "unknown"


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = ""
    services: ServiceStatus = Field(default_factory=ServiceStatus)


# ── Song ─────────────────────────────────────────────────────────

class SongIngestResponse(BaseModel):
    song_id: str
    title: str
    artist: str
    thumbnail: str = ""
    language: str = "Unknown"
    genres: list[str] = Field(default_factory=list)
    cultural_themes: list[str] = Field(default_factory=list)
    mood: str = ""
    era: str = ""
    message: str = "Song ingested successfully"


# ── Transcript ───────────────────────────────────────────────────

class TranscriptResponse(BaseModel):
    transcript_id: str
    song_id: str
    content: str
    source: str = "youtube"


# ── Translation ──────────────────────────────────────────────────

class TranslationResponse(BaseModel):
    translation_id: str
    song_id: str
    target_language: str
    translated_lyrics: str
    translation_notes: str = ""
    confidence_score: float = 0.0


class TranslationListResponse(BaseModel):
    song_id: str
    translations: list[TranslationResponse] = Field(default_factory=list)
    count: int = 0


# ── RAG ──────────────────────────────────────────────────────────

class RAGAskResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    session_id: str = ""
    song_id: str = ""


# ── Error ────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_code: str = "UNKNOWN_ERROR"
