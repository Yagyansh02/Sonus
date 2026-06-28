"""
LLM structured output schemas.

Pydantic models used with ``llm.with_structured_output()`` to replace
all manual JSON parsing.  The Groq API enforces these schemas at the
model level, so no fence-stripping or json.loads() is ever needed.
"""

from pydantic import BaseModel, Field


class SongMetadata(BaseModel):
    """
    Structured output for genre & cultural theme extraction.

    Used in song_processor._extract_metadata_via_llm() with
    llm.with_structured_output(SongMetadata).
    """

    genres: list[str] = Field(
        default_factory=list,
        description="List of music genres (e.g. Hip-Hop, Bollywood Pop, K-Pop, R&B)",
    )
    cultural_themes: list[str] = Field(
        default_factory=list,
        description="2-4 dominant cultural themes (e.g. Heartbreak, Social Justice, Nostalgia)",
    )
    language: str = Field(
        ...,
        description="Full language name of the lyrics (e.g. English, Hindi, Korean, Spanish)",
    )
    mood: str = Field(
        default="",
        description="Overall emotional mood of the song",
    )
    era: str = Field(
        default="",
        description="Approximate musical era or decade (e.g. 1990s, Early 2000s)",
    )


class TranslationResult(BaseModel):
    """
    Structured output for literary lyric translation.

    Used in translation_service.translate_lyrics() with
    llm.with_structured_output(TranslationResult).
    """

    translated_lyrics: str = Field(
        ...,
        description="Full translated lyrics preserving line breaks from the original",
    )
    translation_notes: str = Field(
        default="",
        description="Brief notes on key adaptation choices, cultural swaps, and meaning preservation",
    )
    confidence_score: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in translation quality between 0.0 and 1.0",
    )
