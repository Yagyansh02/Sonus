"""Session domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Session:
    """Represents a conversational RAG session."""

    session_id: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
        }
