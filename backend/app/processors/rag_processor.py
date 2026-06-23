"""
RAG processor.

Orchestrates the conversational retrieval-augmented generation pipeline.
Migrated from the original main.py setup_rag_agent function with
persistent vector retrieval and per-session conversation history.
"""

from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from neo4j import AsyncSession

from app.config.constants import CONTEXTUALIZE_SYSTEM_PROMPT, ETHNOMUSICOLOGIST_SYSTEM_PROMPT
from app.services import groq_service, neo4j_service, vector_service
from app.utils.logger import get_logger
from app.utils.exceptions import SongNotFoundError, RAGProcessingError

logger = get_logger("processors.rag")

# ── In-memory conversation history store ─────────────────────────
# Keyed by "{session_id}:{song_id}" for isolation across songs
_session_memory_store: dict[str, ChatMessageHistory] = {}


def _get_session_history(session_key: str) -> BaseChatMessageHistory:
    """Retrieve or create conversation history for a session+song combination."""
    if session_key not in _session_memory_store:
        _session_memory_store[session_key] = ChatMessageHistory()
    return _session_memory_store[session_key]


# ── Cached RAG chain instances per song ──────────────────────────
_rag_chain_cache: dict[str, RunnableWithMessageHistory] = {}


def _build_rag_chain(song_id: str) -> RunnableWithMessageHistory:
    """
    Build the full conversational RAG chain for a given song.

    Migrated from original main.py setup_rag_agent (lines 113-181).
    """
    logger.info(f"Building RAG chain for song_id={song_id}")

    llm = groq_service.get_llm()
    retriever = vector_service.get_retriever(song_id)

    # ── History-aware retriever ──────────────────────────────────
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", CONTEXTUALIZE_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # ── Ethnomusicologist answer chain ───────────────────────────
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", ETHNOMUSICOLOGIST_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # ── Wrap with message history ────────────────────────────────
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        _get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain


async def ask_question(
    song_id: str,
    session_id: str,
    question: str,
    neo4j_session: AsyncSession,
) -> dict:
    """
    Ask a question about a song using the conversational RAG pipeline.

    Args:
        song_id: ID of the song to query against.
        session_id: Conversation session ID for history tracking.
        question: The user's question.
        neo4j_session: Active Neo4j async session.

    Returns:
        dict with keys: answer, sources, session_id, song_id

    Raises:
        SongNotFoundError: If the song doesn't exist in Neo4j.
        RAGProcessingError: If the RAG pipeline fails.
    """
    # ── Verify song exists ───────────────────────────────────────
    song = await neo4j_service.get_song(neo4j_session, song_id)
    if not song:
        raise SongNotFoundError(song_id)

    # ── Get or build RAG chain ───────────────────────────────────
    if song_id not in _rag_chain_cache:
        try:
            _rag_chain_cache[song_id] = _build_rag_chain(song_id)
        except Exception as e:
            logger.error(f"Failed to build RAG chain for {song_id}: {e}")
            raise RAGProcessingError(f"Could not initialize RAG pipeline: {e}")

    rag_chain = _rag_chain_cache[song_id]

    # ── Link session to song in Neo4j ────────────────────────────
    try:
        await neo4j_service.create_or_get_session(neo4j_session, session_id)
        await neo4j_service.link_session_to_song(neo4j_session, session_id, song_id)
    except Exception as e:
        logger.warning(f"Session tracking failed (non-fatal): {e}")

    # ── Invoke the RAG chain ─────────────────────────────────────
    session_key = f"{session_id}:{song_id}"
    config = {"configurable": {"session_id": session_key}}

    try:
        logger.info(f"RAG query: song={song_id} session={session_id} q='{question[:80]}...'")
        response = rag_chain.invoke({"input": question}, config=config)

        # Extract source chunks
        sources = []
        if "context" in response:
            for doc in response["context"]:
                snippet = doc.page_content[:200].strip()
                if snippet:
                    sources.append(snippet)

        answer = response.get("answer", "I could not generate an answer.")
        logger.info(f"RAG response generated: {len(answer)} chars, {len(sources)} sources")

        return {
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
            "song_id": song_id,
        }

    except Exception as e:
        logger.error(f"RAG processing failed: {e}")
        raise RAGProcessingError(f"Failed to process question: {e}")
