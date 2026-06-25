"""
Vector embedding service.

Provides HuggingFace-based text embedding and lyric chunking,
storing all vectors directly in Neo4j Chunk nodes.

ChromaDB has been fully removed. All vector operations now go through
neo4j_service.store_chunks() and neo4j_service.search_similar_chunks().
"""

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.constants import (
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHUNK_SIZE,
    RETRIEVER_K,
)
from app.config.settings import get_settings
from app.utils.helpers import generate_id
from app.utils.logger import get_logger

logger = get_logger("services.vector")

# Module-level singleton for embeddings (expensive to initialize)
_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Lazy-initialize the HuggingFace embedding model (singleton)."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        logger.info(f"Initializing HuggingFace embeddings: {settings.EMBEDDING_MODEL}")
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


def _chunk_text(content: str, metadata: dict) -> list[Document]:
    """
    Split a transcript into lyric-aware chunks.

    Uses stanza breaks, line breaks, and musical notation markers
    as preferred split points before falling back to word boundaries.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        separators=CHUNK_SEPARATORS,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    doc = Document(page_content=content, metadata=metadata)
    chunks = text_splitter.split_documents([doc])
    logger.info(f"Produced {len(chunks)} lyric chunks")
    return chunks


def chunk_and_embed(
    song_id: str,
    transcript_content: str,
    metadata: dict | None = None,
) -> list[dict]:
    """
    Chunk a transcript and embed each chunk, returning Neo4j-ready dicts.

    Each returned dict has:
        chunk_id    (str)         – unique identifier (UUID hex)
        song_id     (str)         – owning song
        content     (str)         – chunk text
        embedding   (list[float]) – 384-dim HuggingFace vector
        chunk_index (int)         – positional order within the song

    Args:
        song_id:             The owning song's ID (used in metadata).
        transcript_content:  Full transcript text to chunk.
        metadata:            Optional extra metadata attached to each chunk.

    Returns:
        List of chunk dicts ready for neo4j_service.store_chunks().
    """
    doc_metadata: dict = {"song_id": song_id}
    if metadata:
        doc_metadata.update(metadata)

    logger.info(f"Chunking and embedding transcript for song {song_id}")
    chunks = _chunk_text(transcript_content, doc_metadata)

    embedder = get_embeddings()
    texts = [c.page_content for c in chunks]

    # Batch embed all chunks in one call (more efficient than one-by-one)
    vectors = embedder.embed_documents(texts)

    result = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        result.append({
            "chunk_id": generate_id(),
            "song_id": song_id,
            "content": chunk.page_content,
            "embedding": vector,
            "chunk_index": idx,
        })

    logger.info(f"Embedded {len(result)} chunks for song {song_id}")
    return result
