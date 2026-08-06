"""
YouTube data extraction service.

Handles metadata fetching and audio downloading via yt-dlp.
Migrated from the original main.py fetch_video_metadata function.
"""

import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL

from app.utils.logger import get_logger
from app.utils.helpers import extract_video_id
from app.utils.exceptions import YouTubeExtractionError

logger = get_logger("services.youtube")

# Resolves to project root: app/services/youtube_service.py -> app/services -> app/ -> root/
COOKIE_FILE = str(Path(__file__).resolve().parent.parent.parent / "youtube_cookies.txt")


def fetch_video_metadata(video_url: str) -> dict:
    """
    Safely extract video metadata using yt-dlp.

    Returns:
        dict with keys: title, artist, thumbnail
    """
    logger.info(f"Fetching video metadata for: {video_url}")
    ydl_opts = {
    "extract_flat": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": COOKIE_FILE,
    "extractor_args": {"youtube": {"player_client": ["android"]}},
}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            metadata = {
                "title": info.get("title", "Unknown Track"),
                "artist": info.get("uploader", "Unknown Artist"),
                "thumbnail": info.get("thumbnail", ""),
            }
            logger.info(f"Metadata extracted: '{metadata['title']}' by {metadata['artist']}")
            return metadata
    except Exception as e:
        logger.warning(f"Metadata extraction failed: {e}. Using fallback values.")
        return {"title": "Unknown Track", "artist": "Unknown Artist", "thumbnail": ""}


def download_audio(video_url: str) -> Path:
    """
    Download audio from a YouTube video as MP3.

    Returns:
        Path to the downloaded MP3 file in a temp directory.
    """
    video_id = extract_video_id(video_url) or "audio"
    logger.info(f"Downloading audio for video_id={video_id}")

    temp_dir = tempfile.mkdtemp(prefix="sonus_")
    output_path = Path(temp_dir) / f"{video_id}.mp3"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path.with_suffix("")),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "cookiefile": COOKIE_FILE,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if output_path.exists():
            logger.info(f"Audio downloaded: {output_path}")
            return output_path

        for ext in [".mp3", ".m4a", ".webm", ".opus"]:
            alt = output_path.with_suffix(ext)
            if alt.exists():
                logger.info(f"Audio downloaded (alt ext): {alt}")
                return alt

        raise YouTubeExtractionError("Audio file not found after download")

    except YouTubeExtractionError:
        raise
    except Exception as e:
        logger.error(f"Audio download failed: {e}")
        raise YouTubeExtractionError(detail=str(e))