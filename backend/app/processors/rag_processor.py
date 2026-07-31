"""
RAG processor.

Orchestrates the conversational retrieval-augmented generation pipeline.
Uses Neo4j hybrid search (Vector + BM25 full-text) with Reciprocal Rank
Fusion (RRF) for context retrieval -- no ChromaDB, no LangChain retriever
chains. This gives absolute control over prompt context and eliminates the
post-filtering trap of global ANN search.

Pipeline per question:
  1. Verify song exists in Neo4j.
  2. Reformulate the question using chat history (history-aware step).
  3. Embed the reformulated question.
  4. Run hybrid retrieval:
       a. Exact KNN vector search against this song's Chunk nodes.
       b. BM25 full-text search against this song's Chunk nodes.
       c. Merge both ranked lists via Reciprocal Rank Fusion (RRF).
  5. Format retrieved chunks as section-labelled context and invoke the LLM.
  6. Track session in Neo4j (non-fatal).
"""

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from neo4j import AsyncSession

from app.config.constants import (
    BM25_RETRIEVER_K,
    CONTEXTUALIZE_SYSTEM_PROMPT,
    ETHNOMUSICOLOGIST_SYSTEM_PROMPT,
    RETRIEVER_K,
)
from app.services import groq_service, neo4j_service, vector_service
from app.utils.logger import get_logger
from app.utils.exceptions import SongNotFoundError, RAGProcessingError

logger = get_logger("processors.rag")

# -- In-memory conversation history store ------------------------------------
# Keyed by "{session_id}:{song_id}" for isolation across songs
_session_memory_store: dict[str, ChatMessageHistory] = {}

# RRF constant -- higher value reduces the impact of rank differences.
# k=60 is the standard value from the original Cormack et al. (2009) paper.
_RRF_K = 60


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


def _rrf_fuse(
    vector_results: list[dict],
    bm25_results: list[dict],
    k: int = _RRF_K,
) -> list[dict]:
    """
    Merge and re-rank two result lists using Reciprocal Rank Fusion (RRF).

    Formula (Cormack et al., 2009):
        rrf_score(d) = sum_over_lists( 1 / (k + rank_i(d)) )

    where rank_i(d) is the 1-indexed position of document d in list i.
    Documents that appear in both lists receive contributions from both terms,
    naturally surfacing results that are simultaneously semantically relevant
    AND keyword-matching.

    Args:
        vector_results: Chunks ordered by cosine similarity (best first).
        bm25_results:   Chunks ordered by BM25 score (best first).
        k:              RRF constant (default 60 per the original paper).

    Returns:
        De-duplicated, RRF-ranked list of chunk dicts. Each dict contains
        content, chunk_index, section_type, and an rrf_score field.
    """
    # Build a stable key from content + chunk_index to de-duplicate across lists
    scores: dict[str, float] = {}
    chunk_map: dict[str, dict] = {}

    for rank, chunk in enumerate(vector_results, start=1):
        key = f"{chunk['chunk_index']}:{chunk['content'][:40]}"
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        chunk_map[key] = chunk

    for rank, chunk in enumerate(bm25_results, start=1):
        key = f"{chunk['chunk_index']}:{chunk['content'][:40]}"
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        chunk_map[key] = chunk

    # Sort by descending RRF score and annotate
    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for key, rrf_score in fused:
        entry = dict(chunk_map[key])
        entry["rrf_score"] = round(rrf_score, 6)
        result.append(entry)

    return result


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
    # -- 1. Verify song exists ------------------------------------------------
    song = await neo4j_service.get_song(neo4j_session, song_id)
    if not song:
        raise SongNotFoundError(song_id)

    # -- 2. Retrieve / create conversation history ----------------------------
    session_key = f"{session_id}:{song_id}"
    history = _get_session_history(session_key)

    # -- 3. Reformulate question using history --------------------------------
    try:
        reformulated_question = _reformulate_question(question, history)
    except Exception as e:
        logger.warning(f"Reformulation step failed, using original question: {e}")
        reformulated_question = question

    # -- 4. Embed the reformulated question ----------------------------------
    try:
        query_embedding = vector_service.embed_text(reformulated_question)
    except Exception as e:
        logger.error(f"Embedding failed for question: {e}")
        raise RAGProcessingError(f"Failed to embed question: {e}")

    # -- 5a. Vector search (exact KNN) ---------------------------------------
    try:
        vector_chunks = await neo4j_service.search_vector_chunks(
            session=neo4j_session,
            song_id=song_id,
            query_embedding=query_embedding,
            k=RETRIEVER_K,
        )
    except Exception as e:
        logger.error(f"Vector chunk retrieval failed: {e}")
        raise RAGProcessingError(f"Failed to retrieve lyric context (vector): {e}")

    # -- 5b. BM25 full-text search (song-scoped) ------------------------------
    bm25_chunks: list[dict] = []
    try:
        bm25_chunks = await neo4j_service.search_bm25_chunks(
            session=neo4j_session,
            song_id=song_id,
            query_text=reformulated_question,
            k=BM25_RETRIEVER_K,
        )
    except Exception as e:
        # BM25 is non-fatal: if the index doesn't exist yet (e.g. legacy data)
        # or fails, we degrade gracefully to vector-only retrieval.
        logger.warning(f"BM25 search failed (degrading to vector-only): {e}")

    # -- 5c. Merge with Reciprocal Rank Fusion --------------------------------
    if vector_chunks or bm25_chunks:
        fused_chunks = _rrf_fuse(vector_chunks, bm25_chunks)
        chunks = fused_chunks[:RETRIEVER_K]
    else:
        chunks = []

    logger.info(
        f"Hybrid retrieval: vector={len(vector_chunks)} bm25={len(bm25_chunks)} "
        f"-> fused={len(chunks)} chunks for song {song_id}"
    )

    if not chunks:
        logger.warning(
            f"No chunks found for song {song_id}. "
            "Song may not have been ingested with vector embeddings."
        )

    # -- 6. Format section-labelled context and invoke LLM -------------------
    context_text = "\n\n---\n\n".join(
        f"[{c.get('section_type', 'Unknown')} | Chunk {c['chunk_index']}]\n{c['content']}"
        for c in chunks
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

    # -- 7. Persist turn to in-memory history --------------------------------
    history.add_message(HumanMessage(content=question))
    history.add_message(AIMessage(content=answer))

    # -- 8. Track session in Neo4j (non-fatal) --------------------------------
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
