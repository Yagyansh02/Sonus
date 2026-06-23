"""
Tests for the RAG processor and endpoint.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.entities.song import Song


class TestRAGProcessor:
    """Tests for the RAG cultural interpretation pipeline."""

    @pytest.mark.asyncio
    @patch("app.processors.rag_processor.neo4j_service")
    @patch("app.processors.rag_processor.vector_service")
    @patch("app.processors.rag_processor.groq_service")
    async def test_ask_question_song_not_found(
        self, mock_groq, mock_vector, mock_neo4j
    ):
        """Should raise SongNotFoundError when song doesn't exist."""
        from app.processors.rag_processor import ask_question
        from app.utils.exceptions import SongNotFoundError

        mock_neo4j.get_song = AsyncMock(return_value=None)
        mock_session = AsyncMock()

        with pytest.raises(SongNotFoundError):
            await ask_question(
                song_id="nonexistent",
                session_id="test-session",
                question="What does this mean?",
                neo4j_session=mock_session,
            )

    @pytest.mark.asyncio
    @patch("app.processors.rag_processor._build_rag_chain")
    @patch("app.processors.rag_processor.neo4j_service")
    async def test_ask_question_returns_answer(self, mock_neo4j, mock_build_chain):
        """Should return an answer and sources from the RAG pipeline."""
        from app.processors.rag_processor import ask_question, _rag_chain_cache

        # Mock song exists
        mock_song = Song(
            song_id="test123",
            title="Test",
            artist="Artist",
            youtube_url="https://youtube.com/watch?v=test",
        )
        mock_neo4j.get_song = AsyncMock(return_value=mock_song)
        mock_neo4j.create_or_get_session = AsyncMock()
        mock_neo4j.link_session_to_song = AsyncMock()

        # Mock RAG chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "answer": "This lyric means...",
            "context": [],
        }
        mock_build_chain.return_value = mock_chain

        # Clear cache to force rebuild
        _rag_chain_cache.clear()

        mock_session = AsyncMock()
        result = await ask_question(
            song_id="test123",
            session_id="test-session",
            question="What does the chorus mean?",
            neo4j_session=mock_session,
        )

        assert "answer" in result
        assert result["answer"] == "This lyric means..."
        assert "sources" in result
