from pydantic import BaseModel, Field


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


class RAGAskResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    session_id: str = ""
    song_id: str = ""
