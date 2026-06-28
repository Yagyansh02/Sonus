from pydantic import BaseModel, Field, HttpUrl

class SongIngestRequest(BaseModel):
    """Request to ingest a new song from YouTube."""

    youtube_url: HttpUrl = Field(
        ...,
        description="Full YouTube video URL containing the song",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


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
