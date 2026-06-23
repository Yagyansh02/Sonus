"""Transcript domain entity."""

from dataclasses import dataclass


@dataclass
class Transcript:
    """Represents a transcript associated with a song."""

    transcript_id: str
    song_id: str
    content: str
    source: str = "youtube"  # "youtube" | "elevenlabs"

    def to_dict(self) -> dict:
        return {
            "transcript_id": self.transcript_id,
            "song_id": self.song_id,
            "content": self.content,
            "source": self.source,
        }
