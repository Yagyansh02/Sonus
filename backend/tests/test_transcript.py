"""
Tests for the transcript endpoint and processor.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.utils.helpers import extract_video_id


class TestExtractVideoId:
    """Tests for YouTube URL parsing."""

    def test_standard_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_music_url(self):
        url = "https://music.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_invalid_url(self):
        url = "https://example.com/not-youtube"
        assert extract_video_id(url) is None

    def test_url_with_extra_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


class TestTranscriptProcessor:
    """Tests for the transcript fallback pipeline."""

    @patch("app.processors.transcript_processor.transcript_service")
    def test_youtube_transcript_success(self, mock_service):
        """Should return YouTube transcript when available."""
        from langchain_core.documents import Document
        from app.processors.transcript_processor import get_transcript

        mock_doc = Document(page_content="Hello world lyrics")
        mock_service.fetch_youtube_transcript.return_value = [mock_doc]

        content, source = get_transcript("https://youtube.com/watch?v=test", "test_id")

        assert content == "Hello world lyrics"
        assert source == "youtube"

    @patch("app.processors.transcript_processor.elevenlabs_service")
    @patch("app.processors.transcript_processor.youtube_service")
    @patch("app.processors.transcript_processor.transcript_service")
    def test_fallback_to_elevenlabs(self, mock_transcript, mock_youtube, mock_elevenlabs):
        """Should fall back to ElevenLabs when YouTube transcript unavailable."""
        from pathlib import Path
        from app.processors.transcript_processor import get_transcript

        mock_transcript.fetch_youtube_transcript.return_value = None
        mock_youtube.download_audio.return_value = Path("/tmp/test.mp3")
        mock_elevenlabs.transcribe_audio.return_value = "Fallback transcript text"

        with patch("shutil.rmtree"):
            with patch.object(Path, "exists", return_value=True):
                content, source = get_transcript("https://youtube.com/watch?v=test", "test_id")

        assert content == "Fallback transcript text"
        assert source == "elevenlabs"
