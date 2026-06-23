"""
Tests for the translation service and endpoint.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestTranslationService:
    """Tests for the literary translation service."""

    @patch("app.services.translation_service.get_llm")
    def test_translate_lyrics_success(self, mock_get_llm):
        """Should parse a valid JSON translation response from the LLM."""
        from app.services.translation_service import translate_lyrics

        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "translated_lyrics": "अनुवादित गीत",
            "translation_notes": "Preserved the metaphor of rain as sadness",
            "confidence_score": 0.92,
        })

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = translate_lyrics("Some English lyrics here", "Hindi")

        assert result["translated_lyrics"] == "अनुवादित गीत"
        assert result["confidence_score"] == 0.92
        assert "notes" in result["translation_notes"].lower() or len(result["translation_notes"]) > 0

    @patch("app.services.translation_service.get_llm")
    def test_translate_lyrics_handles_markdown_fences(self, mock_get_llm):
        """Should handle LLM responses wrapped in markdown code fences."""
        from app.services.translation_service import translate_lyrics

        mock_response = MagicMock()
        mock_response.content = '```json\n{"translated_lyrics": "Test", "translation_notes": "", "confidence_score": 0.8}\n```'

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = translate_lyrics("Lyrics", "Spanish")
        assert result["translated_lyrics"] == "Test"

    @patch("app.services.translation_service.get_llm")
    def test_translate_lyrics_raises_on_invalid_json(self, mock_get_llm):
        """Should raise TranslationError when LLM returns invalid JSON."""
        from app.services.translation_service import translate_lyrics
        from app.utils.exceptions import TranslationError

        mock_response = MagicMock()
        mock_response.content = "This is not JSON at all"

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        with pytest.raises(TranslationError):
            translate_lyrics("Lyrics", "Hindi")
