"""
Utility helpers for URL parsing, ID generation, and text processing.
"""

import re
import uuid
from urllib.parse import parse_qs, urlparse


def generate_id() -> str:
    """Generate a unique identifier (UUID4 hex, no dashes)."""
    return uuid.uuid4().hex


def extract_video_id(url: str) -> str | None:
    """
    Extract the YouTube video ID from various URL formats.

    Supports:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/embed/VIDEO_ID
      - https://music.youtube.com/watch?v=VIDEO_ID
    """
    parsed = urlparse(url)

    # youtu.be short links
    if parsed.hostname and "youtu.be" in parsed.hostname:
        return parsed.path.lstrip("/").split("/")[0] or None

    # Standard and embed URLs
    if parsed.hostname and "youtube" in parsed.hostname:
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else None
        qs = parse_qs(parsed.query)
        video_ids = qs.get("v")
        if video_ids:
            return video_ids[0]

    return None


def sanitize_collection_name(name: str) -> str:
    """
    Sanitize a string for use as a Chroma collection name.

    Chroma requires: 3-63 chars, starts/ends with alphanumeric,
    only contains alphanumeric, underscores, or hyphens.
    """
    # Replace non-alphanumeric chars with underscores
    clean = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Strip leading/trailing non-alphanumeric
    clean = clean.strip("_-")
    # Ensure minimum length
    if len(clean) < 3:
        clean = f"col_{clean}"
    # Truncate to max length
    return clean[:63]


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
