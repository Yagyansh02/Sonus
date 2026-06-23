"""
Transcript processor.

Orchestrates transcript retrieval with automatic fallback:
  1. Try YouTube captions via YoutubeLoader
  2. If unavailable → download audio via yt-dlp → ElevenLabs STT
"""

import shutil
from pathlib import Path

from langchain_core.documents import Document

from app.services import transcript_service, youtube_service, elevenlabs_service
from app.utils.logger import get_logger
from app.utils.exceptions import TranscriptNotFoundError

logger = get_logger("processors.transcript")


def get_transcript(video_url: str, song_id: str) -> tuple[str, str]:
    """
    Retrieve a transcript for the given video, with automatic fallback.

    Pipeline:
      Step 1: Attempt YoutubeLoader (captions/subtitles).
      Step 2: If no captions → download audio via yt-dlp.
      Step 3: Send audio to ElevenLabs Scribe v2 for STT.
      Step 4: Clean up temp audio files.

    Args:
        video_url: Full YouTube URL.
        song_id: Used for logging context.

    Returns:
        Tuple of (transcript_content, source) where source is
        "youtube" or "elevenlabs".

    Raises:
        TranscriptNotFoundError: If both sources fail.
    """
    # ── Step 1: Try YouTube captions ─────────────────────────────
    logger.info(f"[{song_id}] Attempting YouTube transcript extraction")
    documents = transcript_service.fetch_youtube_transcript(video_url)

    if documents:
        content = "\n".join(doc.page_content for doc in documents)
        if content.strip():
            logger.info(f"[{song_id}] YouTube transcript acquired ({len(content)} chars)")
            return content, "youtube"

    # ── Step 2-3: Fallback to ElevenLabs STT ─────────────────────
    logger.warning(f"[{song_id}] YouTube transcript unavailable, activating ElevenLabs fallback")

    audio_path: Path | None = None
    try:
        # Download audio
        audio_path = youtube_service.download_audio(video_url)
        logger.info(f"[{song_id}] Audio downloaded: {audio_path}")

        # Transcribe via ElevenLabs
        content = elevenlabs_service.transcribe_audio(audio_path)
        logger.info(f"[{song_id}] ElevenLabs transcript acquired ({len(content)} chars)")
        return content, "elevenlabs"

    except Exception as e:
        logger.error(f"[{song_id}] All transcript sources failed: {e}")
        raise TranscriptNotFoundError(
            f"Could not obtain transcript for {video_url}. "
            f"YouTube captions unavailable and ElevenLabs fallback failed: {e}"
        )
    finally:
        # ── Step 4: Cleanup temp audio ───────────────────────────
        if audio_path and audio_path.exists():
            try:
                shutil.rmtree(audio_path.parent, ignore_errors=True)
                logger.info(f"[{song_id}] Temp audio cleaned up")
            except Exception:
                pass


def get_transcript_as_documents(
    video_url: str, song_id: str, metadata: dict | None = None
) -> list[Document]:
    """
    Retrieve transcript and return as LangChain Documents ready for vectorization.

    Args:
        video_url: Full YouTube URL.
        song_id: For logging and metadata.
        metadata: Additional metadata to attach to each Document.

    Returns:
        List of LangChain Documents with enriched metadata.
    """
    content, source = get_transcript(video_url, song_id)

    doc_metadata = {"song_id": song_id, "source": source}
    if metadata:
        doc_metadata.update(metadata)

    return [Document(page_content=content, metadata=doc_metadata)]
