"""
Transcript extraction service.

Wraps LangChain's YoutubeLoader for transcript retrieval.
Migrated from the original main.py fetch_youtube_transcript function.
"""

from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document

from app.utils.logger import get_logger

logger = get_logger("services.transcript")


def fetch_youtube_transcript(video_url: str) -> list[Document] | None:
    """
    Attempt to load transcripts/captions from YouTube using LangChain.

    Migrated from original main.py lines 56-82 (loader portion only;
    metadata enrichment is handled by the processor layer).

    Args:
        video_url: Full YouTube video URL.

    Returns:
        List of LangChain Documents if successful, None if no transcript
        is available.
    """
    logger.info(f"Attempting YouTube transcript extraction for: {video_url}")

    try:
        loader = YoutubeLoader.from_youtube_url(
            video_url,
            add_video_info=False,
            language=["en", "hi", "es", "fr", "de", "ja", "ko", "pt", "zh"],
        )
        documents = loader.load()

        if not documents:
            logger.warning("YoutubeLoader returned no documents")
            return None

        # Log a preview of what was loaded
        content_preview = documents[0].page_content[:100]
        logger.info(f"Transcript loaded ({len(documents)} doc(s)): '{content_preview}...'")
        return documents

    except Exception as e:
        logger.warning(f"YouTube transcript extraction failed: {e}")
        return None
