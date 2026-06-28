from pydantic import BaseModel, Field, HttpUrl


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
