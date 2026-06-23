"""Song domain entity."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Song:
    """Represents a song ingested into the system."""

    song_id: str
    title: str
    artist: str
    youtube_url: str
    thumbnail: str = ""
    language: str = "Unknown"
    genres: list[str] = field(default_factory=list)
    cultural_themes: list[str] = field(default_factory=list)
    mood: str = ""
    era: str = ""

    def to_dict(self) -> dict:
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "youtube_url": self.youtube_url,
            "thumbnail": self.thumbnail,
            "language": self.language,
            "genres": self.genres,
            "cultural_themes": self.cultural_themes,
            "mood": self.mood,
            "era": self.era,
        }
