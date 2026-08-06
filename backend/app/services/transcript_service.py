"""
Transcript extraction service.

Wraps youtube_transcript_api directly for transcript retrieval, 
bypassing LangChain's loader to allow cookie authentication.
"""

from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document

from app.utils.logger import get_logger
from app.utils.helpers import extract_video_id

logger = get_logger("services.transcript")

# Resolves to project root: app/services/transcript_service.py -> app/services -> app/ -> root/
COOKIE_FILE = str(Path(__file__).resolve().parent.parent.parent / "youtube_cookies.txt")

def fetch_youtube_transcript(video_url: str) -> list[Document] | None:
    logger.info(f"Attempting YouTube transcript extraction for: {video_url}")
    video_id = extract_video_id(video_url)

    if not video_id:
        logger.warning(f"Could not extract video ID from url: {video_url}")
        return None

    try:
        ytt_api = YouTubeTranscriptApi() 
        fetched = ytt_api.fetch(
            video_id,
            languages=["en", "hi", "es", "fr", "de", "ja", "ko", "pt", "zh"],
        )

        # fetched is a FetchedTranscript (iterable of snippets with .text)
        full_text = " ".join(snippet.text for snippet in fetched)

        documents = [Document(page_content=full_text)]
        content_preview = documents[0].page_content[:100]
        logger.info(f"Transcript loaded (1 doc(s)): '{content_preview}...'")
        return documents

    except Exception as e:
        logger.warning(f"YouTube transcript extraction failed: {e}")
        return None
    """
    Attempt to load transcripts/captions from YouTube using youtube_transcript_api directly.

    Returns:
        List of LangChain Documents if successful, None if no transcript is available.
    """
    logger.info(f"Attempting YouTube transcript extraction for: {video_url}")
    video_id = extract_video_id(video_url)
    
    if not video_id:
        logger.warning(f"Could not extract video ID from url: {video_url}")
        return None

    try:
        # Fetch transcript directly using cookies
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=["en", "hi", "es", "fr", "de", "ja", "ko", "pt", "zh"],
            cookies=COOKIE_FILE
        )
        
        # Combine text from transcript segments
        full_text = " ".join([item['text'] for item in transcript_list])
        
        # Return as a LangChain Document to match the processor pipeline
        documents = [Document(page_content=full_text)]
        
        content_preview = documents[0].page_content[:100]
        logger.info(f"Transcript loaded (1 doc(s)): '{content_preview}...'")
        
        return documents

    except Exception as e:
        logger.warning(f"YouTube transcript extraction failed: {e}")
        return None