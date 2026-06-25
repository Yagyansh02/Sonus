"""
RAG processor.

Orchestrates the conversational retrieval-augmented generation pipeline.
Uses Neo4j exact KNN graph traversal for context retrieval — no ChromaDB,
no LangChain retriever chains. This gives absolute control over prompt
context and eliminates the post-filtering trap of global ANN search.

Pipeline per question:
  1. Verify song exists in Neo4j.
  2. Reformulate the question using chat history (history-aware step).
  3. Embed the reformulated question.
  4. Run exact KNN against this song's Chunk nodes in Neo4j.
  5. Format retrieved chunks as context and invoke the LLM.
  6. Track session in Neo4j (non-fatal).
"""

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from neo4j import AsyncSession

from app.config.constants import (
    CONTEXTUALIZE_SYSTEM_PROMPT,
    ETHNOMUSICOLOGIST_SYSTEM_PROMPT,
    RETRIEVER_K,
)
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


def _reformulate_question(question: str, history: ChatMessageHistory) -> str:
    """
    Use the LLM to reformulate the user's question into a self-contained query
    that resolves pronouns and implicit references from chat history.

    If there is no prior history, the original question is returned unchanged
    to avoid an unnecessary LLM call.
    """
    messages = history.messages
    if not messages:
        return question

    llm = groq_service.get_llm(temperature=0.0)

    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", CONTEXTUALIZE_SYSTEM_PROMPT),
        *[(msg.type, msg.content) for msg in messages],
        ("human", "{input}"),
    ])

    chain = contextualize_prompt | llm
    try:
        response = chain.invoke({"input": question})
        reformulated = response.content.strip()
        if reformulated:
            logger.debug(f"Reformulated question: '{reformulated[:120]}'")
            return reformulated
    except Exception as e:
        logger.warning(f"Question reformulation failed (using original): {e}")

    return question


async def ask_question(
    song_id: str,
    session_id: str,
    question: str,
    neo4j_session: AsyncSession,
) -> dict:
    """
    Ask a question about a song using the conversational RAG pipeline.

    Args:
        song_id:       ID of the song to query against.
        session_id:    Conversation session ID for history tracking.
        question:      The user's question.
        neo4j_session: Active Neo4j async session.

    Returns:
        dict with keys: answer, sources, session_id, song_id

    Raises:
        SongNotFoundError:  If the song doesn't exist in Neo4j.
        RAGProcessingError: If the RAG pipeline fails.
    """
    # ── 1. Verify song exists ────────────────────────────────────
    song = await neo4j_service.get_song(neo4j_session, song_id)
    if not song:
        raise SongNotFoundError(song_id)

    # ── 2. Retrieve / create conversation history ────────────────
    session_key = f"{session_id}:{song_id}"
    history = _get_session_history(session_key)

    # ── 3. Reformulate question using history ────────────────────
    try:
        reformulated_question = _reformulate_question(question, history)
    except Exception as e:
        logger.warning(f"Reformulation step failed, using original question: {e}")
        reformulated_question = question

    # ── 4. Embed the reformulated question ───────────────────────
    try:
        query_embedding = vector_service.embed_text(reformulated_question)
    except Exception as e:
        logger.error(f"Embedding failed for question: {e}")
        raise RAGProcessingError(f"Failed to embed question: {e}")

    # ── 5. Exact KNN: retrieve top-k chunks from Neo4j ───────────
    try:
        chunks = await neo4j_service.search_similar_chunks(
            session=neo4j_session,
            song_id=song_id,
            query_embedding=query_embedding,
            k=RETRIEVER_K,
        )
    except Exception as e:
        logger.error(f"Chunk retrieval failed: {e}")
        raise RAGProcessingError(f"Failed to retrieve lyric context: {e}")

    if not chunks:
        logger.warning(
            f"No chunks found for song {song_id}. "
            "Song may not have been ingested with vector embeddings."
        )

    # ── 6. Format context and invoke LLM ────────────────────────
    context_text = "\n\n---\n\n".join(
        f"[Chunk {c['chunk_index']}]\n{c['content']}" for c in chunks
    ) if chunks else "No lyric context available."

    # Inline the system prompt with context (replaces {context} placeholder)
    system_with_context = ETHNOMUSICOLOGIST_SYSTEM_PROMPT.replace(
        "{context}", context_text
    )

    llm = groq_service.get_llm()

    # Build the full message list: system + history + current question
    history_messages = history.messages
    messages = [("system", system_with_context)]
    for msg in history_messages:
        messages.append((msg.type, msg.content))
    messages.append(("human", question))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm

    try:
        logger.info(
            f"RAG query: song={song_id} session={session_id} "
            f"chunks={len(chunks)} q='{question[:80]}...'"
        )
        response = chain.invoke({})
        answer = response.content.strip() or "I could not generate an answer."
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        raise RAGProcessingError(f"Failed to process question: {e}")

    # ── 7. Persist turn to in-memory history ────────────────────
    history.add_message(HumanMessage(content=question))
    history.add_message(AIMessage(content=answer))

    # ── 8. Track session in Neo4j (non-fatal) ───────────────────
    try:
        await neo4j_service.create_or_get_session(neo4j_session, session_id)
        await neo4j_service.link_session_to_song(neo4j_session, session_id, song_id)
    except Exception as e:
        logger.warning(f"Session tracking failed (non-fatal): {e}")

    sources = [c["content"][:200].strip() for c in chunks if c["content"].strip()]

    logger.info(f"RAG response generated: {len(answer)} chars, {len(sources)} sources")

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "song_id": song_id,
    }
