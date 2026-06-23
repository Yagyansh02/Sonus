"""
Pydantic request models for API validation.

Every incoming request body is validated through these schemas
before reaching the processor layer.
"""

from pydantic import BaseModel, Field, HttpUrl


class SongIngestRequest(BaseModel):
    """Request to ingest a new song from YouTube."""

    youtube_url: HttpUrl = Field(
        ...,
        description="Full YouTube video URL containing the song",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


class TranslateRequest(BaseModel):
    """Request to translate a song's lyrics into a target language."""

    song_id: str | None = Field(
        default=None,
        description="ID of an already-ingested song. Provide either this or youtube_url.",
    )
    youtube_url: HttpUrl | None = Field(
        default=None,
        description="YouTube URL to ingest and translate. Provide either this or song_id.",
    )
    target_language: str = Field(
        ...,
        description="Target language for translation",
        examples=["Hindi", "Spanish", "Japanese"],
    )


class RAGAskRequest(BaseModel):
    """Request to ask a question about a song using the RAG pipeline."""

    song_id: str = Field(
        ...,
        description="ID of the song to query against",
    )
    session_id: str = Field(
        ...,
        description="Conversation session ID for history tracking",
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The question to ask about the song",
        examples=["What does the chorus mean?", "Explain the cultural references"],
    )
