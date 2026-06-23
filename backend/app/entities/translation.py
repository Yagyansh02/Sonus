"""Translation domain entity."""

from dataclasses import dataclass


@dataclass
class Translation:
    """Represents a translated version of song lyrics."""

    translation_id: str
    song_id: str
    target_language: str
    translated_lyrics: str
    notes: str = ""
    confidence_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "translation_id": self.translation_id,
            "song_id": self.song_id,
            "target_language": self.target_language,
            "translated_lyrics": self.translated_lyrics,
            "notes": self.notes,
            "confidence_score": self.confidence_score,
        }
