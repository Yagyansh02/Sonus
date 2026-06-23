"""User query domain entity."""

from dataclasses import dataclass, field


@dataclass
class UserQuery:
    """Represents a single question/answer exchange within a session."""

    query_id: str
    session_id: str
    song_id: str
    question: str
    answer: str = ""
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "session_id": self.session_id,
            "song_id": self.song_id,
            "question": self.question,
            "answer": self.answer,
            "sources": self.sources,
        }
