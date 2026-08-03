"""
Vector embedding service.

Provides HuggingFace-based text embedding and structure-aware lyric chunking,
storing all vectors directly in Neo4j Chunk nodes.

ChromaDB has been fully removed. All vector operations now go through
neo4j_service.store_chunks() and neo4j_service.search_similar_chunks().

Chunking strategy:
  1. lyrics_structurizer.tag_song_structure() segments the transcript into
     labelled musical sections (Verse 1, Chorus, Bridge, etc.) using Groq.
  2. RecursiveCharacterTextSplitter is applied WITHIN each section boundary,
     so recurring units like choruses are never split across thematic contexts.
  3. Each LyricChunk carries a section_type field for context-aware retrieval.
"""

from typing import Any
import httpx
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.constants import (
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHUNK_SIZE,
)
from app.config.settings import get_settings
from app.schemas.chunk import LyricChunk
from app.services import lyrics_structurizer
from app.utils.helpers import generate_id
from app.utils.exceptions import ExternalServiceError
from app.utils.logger import get_logger

logger = get_logger("services.vector")


class HuggingFaceAPIEmbeddings:
    """Embeddings runner that calls Hugging Face Inference Providers API directly."""

    def __init__(self, model_name: str, hf_token: str):
        if "/" not in model_name:
            self.model_id = f"sentence-transformers/{model_name}"
        else:
            self.model_id = model_name
        # Old api-inference.huggingface.co is dead (410 Gone) — use the new router
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_id}/pipeline/feature-extraction"
        self.headers = {"Authorization": f"Bearer {hf_token}"}

    def _call_api(self, texts: list[str] | str) -> Any:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": texts, "options": {"wait_for_model": True}},
                )
                if response.status_code != 200:
                    raise ExternalServiceError(
                        service="Hugging Face",
                        detail=f"Hugging Face API error ({response.status_code}): {response.text}"
                    )
                return response.json()
        except Exception as e:
            logger.error(f"Hugging Face API connection failed: {e}")
            if isinstance(e, ExternalServiceError):
                raise e
            raise ExternalServiceError(
                service="Hugging Face",
                detail=f"Hugging Face API connection failed: {str(e)}"
            )

    def embed_query(self, text: str) -> list[float]:
        result = self._call_api(text)
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                return result[0]
            return result
        raise ExternalServiceError(
            service="Hugging Face",
            detail="Invalid response format from Hugging Face API"
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result = self._call_api(texts)
        if isinstance(result, list):
            return result
        raise ExternalServiceError(
            service="Hugging Face",
            detail="Invalid response format from Hugging Face API"
        )


# Module-level singleton for embeddings (expensive to initialize)
_embeddings: Any = None


def get_embeddings() -> Any:
    """Lazy-initialize the HuggingFace embedding model (singleton)."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        if settings.HF_TOKEN:
            logger.info("Initializing HuggingFace API Embeddings (Remote Inference)")
            _embeddings = HuggingFaceAPIEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                hf_token=settings.HF_TOKEN,
            )
        else:
            logger.info(f"Initializing HuggingFace Embeddings (Local): {settings.EMBEDDING_MODEL}")
            from langchain_huggingface import HuggingFaceEmbeddings
            _embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    return _embeddings


def embed_text(text: str) -> list[float]:
    """
    Embed a single string into a 384-dimensional vector.

    Args:
        text: The text to embed.

    Returns:
        A list of 384 floats representing the semantic embedding.
    """
    embeddings = get_embeddings()
    return embeddings.embed_query(text)


def _split_section(text: str, metadata: dict) -> list[Document]:
    """
    Apply RecursiveCharacterTextSplitter within the boundaries of a single
    musical section.  Reuses the shared chunking config from constants.py.

    Args:
        text:     The section lyrics text.
        metadata: Metadata dict already containing song_id and section_type.

    Returns:
        List of LangChain Documents, each representing a sub-chunk of the section.
    """
    splitter = RecursiveCharacterTextSplitter(
        separators=CHUNK_SEPARATORS,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    doc = Document(page_content=text, metadata=metadata)
    return splitter.split_documents([doc])


def chunk_and_embed(
    song_id: str,
    transcript_content: str,
    metadata: dict | None = None,
) -> list[LyricChunk]:
    """
    Chunk a transcript structurally and embed each chunk.

    Pipeline:
      1. Call lyrics_structurizer.tag_song_structure() to get labelled sections.
      2. For each section, apply RecursiveCharacterTextSplitter within the section
         boundary (preserves thematic units like choruses).
      3. Batch-embed all resulting chunks in a single HuggingFace call.
      4. Return typed LyricChunk DTOs ready for neo4j_service.store_chunks().

    Each returned LyricChunk has:
        chunk_id     (str)         -- unique identifier (UUID hex)
        song_id      (str)         -- owning song
        content      (str)         -- chunk text
        embedding    (list[float]) -- 384-dim HuggingFace vector
        chunk_index  (int)         -- positional order within the song
        section_type (str)         -- musical section label (e.g. "Chorus")

    Args:
        song_id:             The owning song ID.
        transcript_content:  Full transcript text to chunk.
        metadata:            Optional extra metadata attached to each chunk.

    Returns:
        List of LyricChunk DTOs ready for neo4j_service.store_chunks().
    """
    base_metadata: dict = {"song_id": song_id}
    if metadata:
        base_metadata.update(metadata)

    logger.info(f"Starting structural chunking for song {song_id}")

    # -- 1. Tag song structure via Groq -----------------------------------------
    sections = lyrics_structurizer.tag_song_structure(transcript_content)

    if not sections:
        logger.warning(f"[{song_id}] No sections returned -- skipping embed")
        return []

    logger.info(f"[{song_id}] {len(sections)} sections to chunk")

    # -- 2. Split within each section boundary -----------------------------------
    all_documents: list[tuple[Document, str]] = []  # (doc, section_type)
    for section in sections:
        if not section.lyrics.strip():
            continue

        section_meta = {**base_metadata, "section_type": section.section_type}
        sub_docs = _split_section(section.lyrics, section_meta)

        for doc in sub_docs:
            all_documents.append((doc, section.section_type))

    if not all_documents:
        logger.warning(f"[{song_id}] All sections were empty after splitting")
        return []

    logger.info(f"[{song_id}] Produced {len(all_documents)} chunks across all sections")

    # -- 3. Batch embed ----------------------------------------------------------
    embedder = get_embeddings()
    texts = [doc.page_content for doc, _ in all_documents]
    vectors = embedder.embed_documents(texts)

    # -- 4. Build LyricChunk DTOs ------------------------------------------------
    result: list[LyricChunk] = [
        LyricChunk(
            chunk_id=generate_id(),
            song_id=song_id,
            content=doc.page_content,
            embedding=vector,
            chunk_index=idx,
            section_type=section_type,
        )
        for idx, ((doc, section_type), vector) in enumerate(zip(all_documents, vectors))
    ]

    logger.info(
        f"[{song_id}] Embedded {len(result)} chunks -- "
        f"sections: {', '.join(s.section_type for s in sections)}"
    )
    return result
