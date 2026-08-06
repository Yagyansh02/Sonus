"""
Transcript extraction service.

Wraps youtube_transcript_api directly for transcript retrieval.

NOTE: youtube_transcript_api v1.x removed the old static methods
(get_transcript / get_transcripts / list_transcripts) in favor of an
instance-based API (`YouTubeTranscriptApi().fetch(...)`). Cookie-based
auth is also no longer accepted as a kwarg on fetch() in this version,
so we no longer pass COOKIE_FILE here — YouTube-side auth for transcripts
now happens (if at all) via the session's own cookie jar, not this param.
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from langchain_core.documents import Document

from app.utils.logger import get_logger
from app.utils.helpers import extract_video_id

logger = get_logger("services.transcript")

LANGUAGES = ["en", "hi", "es", "fr", "de", "ja", "ko", "pt", "zh"]


def fetch_youtube_transcript(video_url: str) -> list[Document] | None:
    """
    Attempt to load transcripts/captions from YouTube using youtube_transcript_api.

    Returns:
        List of LangChain Documents if successful, None if no transcript is available.
    """
    logger.info(f"Attempting YouTube transcript extraction for: {video_url}")
    video_id = extract_video_id(video_url)

    if not video_id:
        logger.warning(f"Could not extract video ID from url: {video_url}")
        return None

    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id, languages=LANGUAGES)

        # fetched is a FetchedTranscript: iterable of snippets, each with .text
        full_text = " ".join(snippet.text for snippet in fetched if snippet.text)

        if not full_text.strip():
            logger.warning(f"Transcript for {video_id} was empty after joining segments.")
            return None

        documents = [Document(page_content=full_text)]

        content_preview = documents[0].page_content[:100]
        logger.info(
            f"Transcript loaded for {video_id} "
            f"({len(fetched)} segments, {len(full_text)} chars): '{content_preview}...'"
        )
        return documents

    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        # Expected, non-noisy cases — no transcript exists for this video/language set.
        logger.info(f"No transcript available for {video_id}: {e}")
        return None

    except Exception as e:
        # Anything else (network issues, library-internal errors, etc.) — log with
        # enough context to debug, then let the caller fall back to ElevenLabs.
        logger.warning(f"YouTube transcript extraction failed for {video_id}: {e}")
        return None