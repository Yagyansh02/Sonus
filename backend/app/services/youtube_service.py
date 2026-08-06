"""
YouTube data extraction service.

Handles metadata fetching and audio downloading via yt-dlp.

YouTube periodically breaks specific yt-dlp "player clients" (web, mweb,
android, etc.) as it rolls out new JS challenges / PO-token requirements.
Rather than hard-failing on the first client that YouTube has currently
broken, we try a short list of clients in order and only give up once
all of them fail. This makes the service resilient to the kind of
"The page needs to be reloaded." / bot-check errors that come and go
as yt-dlp's extractors catch up with YouTube-side changes.
"""

import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.version import __version__ as YTDLP_VERSION

from app.utils.logger import get_logger
from app.utils.helpers import extract_video_id
from app.utils.exceptions import YouTubeExtractionError

logger = get_logger("services.youtube")

# Resolves to project root: app/services/youtube_service.py -> app/services -> app/ -> root/
COOKIE_FILE = str(Path(__file__).resolve().parent.parent.parent / "youtube_cookies.txt")

# Order matters: try clients least likely to be currently rate-limited /
# challenge-broken first. Adjust this list if you see a specific client
# reliably failing in your logs — that's a sign YouTube has broken it and
# it's worth demoting or dropping until yt-dlp patches it.
CLIENT_FALLBACKS = ["android_vr", "android", "tv", "web"]


def _cookie_file_if_present() -> str | None:
    """Only pass a cookiefile to yt-dlp if it actually exists and is non-empty."""
    path = Path(COOKIE_FILE)
    if path.exists() and path.stat().st_size > 0:
        return COOKIE_FILE
    logger.warning(f"No usable cookie file at {COOKIE_FILE}; proceeding without cookies.")
    return None


def _base_opts() -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
    }
    cookie_file = _cookie_file_if_present()
    if cookie_file:
        opts["cookiefile"] = cookie_file
    return opts


def fetch_video_metadata(video_url: str) -> dict:
    """
    Safely extract video metadata using yt-dlp, trying multiple player
    clients in order until one succeeds.

    Returns:
        dict with keys: title, artist, thumbnail
    """
    logger.info(f"Fetching video metadata for: {video_url} (yt-dlp {YTDLP_VERSION})")

    last_error: Exception | None = None

    for client in CLIENT_FALLBACKS:
        ydl_opts = {
            **_base_opts(),
            "extract_flat": True,
            "extractor_args": {"youtube": {"player_client": [client]}},
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                metadata = {
                    "title": info.get("title", "Unknown Track"),
                    "artist": info.get("uploader", "Unknown Artist"),
                    "thumbnail": info.get("thumbnail", ""),
                }
                logger.info(
                    f"Metadata extracted via client='{client}': "
                    f"'{metadata['title']}' by {metadata['artist']}"
                )
                return metadata
        except Exception as e:
            logger.warning(f"Metadata extraction failed for client='{client}': {e}")
            last_error = e

    logger.warning(
        f"Metadata extraction failed for all clients {CLIENT_FALLBACKS}. "
        f"Last error: {last_error}. Using fallback values. "
        f"If this persists, check `pip install -U yt-dlp` and cookie freshness."
    )
    return {"title": "Unknown Track", "artist": "Unknown Artist", "thumbnail": ""}


def download_audio(video_url: str) -> Path:
    """
    Download audio from a YouTube video as MP3, trying multiple player
    clients in order until one succeeds.

    Returns:
        Path to the downloaded MP3 file in a temp directory.
    """
    video_id = extract_video_id(video_url) or "audio"
    logger.info(f"Downloading audio for video_id={video_id} (yt-dlp {YTDLP_VERSION})")

    temp_dir = tempfile.mkdtemp(prefix="sonus_")
    output_path = Path(temp_dir) / f"{video_id}.mp3"

    last_error: Exception | None = None

    for client in CLIENT_FALLBACKS:
        ydl_opts = {
            **_base_opts(),
            "format": "bestaudio/best",
            "outtmpl": str(output_path.with_suffix("")),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
            "extractor_args": {"youtube": {"player_client": [client]}},
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            if output_path.exists():
                logger.info(f"Audio downloaded via client='{client}': {output_path}")
                return output_path

            for ext in [".mp3", ".m4a", ".webm", ".opus"]:
                alt = output_path.with_suffix(ext)
                if alt.exists():
                    logger.info(f"Audio downloaded via client='{client}' (alt ext): {alt}")
                    return alt

            logger.warning(f"Download reported success but no output file found for client='{client}'.")

        except Exception as e:
            logger.warning(f"Audio download failed for client='{client}': {e}")
            last_error = e

    logger.error(
        f"Audio download failed for all clients {CLIENT_FALLBACKS} "
        f"on video_id={video_id}. Last error: {last_error}"
    )
    raise YouTubeExtractionError(detail=str(last_error) if last_error else "Audio file not found after download")