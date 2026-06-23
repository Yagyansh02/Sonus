"""
Persistent vector store service.

Manages Chroma collections with HuggingFace embeddings.
Refactored from the original main.py create_vector_store function
with persistence and collection-per-song isolation.
"""

from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.constants import (
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHUNK_SIZE,
    RETRIEVER_K,
)
from app.config.settings import get_settings
from app.utils.helpers import sanitize_collection_name
from app.utils.logger import get_logger
from app.utils.exceptions import VectorStoreError

logger = get_logger("services.vector")

# Module-level singleton for embeddings (expensive to initialize)
_embeddings: HuggingFaceEmbeddings | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Lazy-initialize the HuggingFace embedding model (singleton)."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        logger.info(f"Initializing HuggingFace embeddings: {settings.EMBEDDING_MODEL}")
        _embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    return _embeddings


def _get_persist_dir() -> str:
    """Return the Chroma persistence directory, creating it if needed."""
    settings = get_settings()
    persist_dir = Path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)
    return str(persist_dir)


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into lyric-aware chunks.

    Migrated from original main.py lines 86-96.
    """
    logger.info("Chunking documents into verse contexts")

    text_splitter = RecursiveCharacterTextSplitter(
        separators=CHUNK_SEPARATORS,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Produced {len(chunks)} contextual lyric chunks")
    return chunks


def create_or_load_index(song_id: str, documents: list[Document] | None = None) -> Chroma:
    """
    Create a new Chroma collection for a song, or load an existing one.

    If ``documents`` is provided and the collection doesn't exist yet,
    a new collection is created from the chunked documents.
    If the collection already exists, it is loaded regardless of
    whether documents are provided.

    Args:
        song_id:    Unique song identifier used as the collection name.
        documents:  Raw LangChain Documents to chunk and index (optional).

    Returns:
        A Chroma vector store instance.
    """
    collection_name = sanitize_collection_name(f"song_{song_id}")
    embeddings = _get_embeddings()
    persist_dir = _get_persist_dir()

    try:
        # Try to load existing collection
        existing = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        # Check if collection has data
        count = existing._collection.count()
        if count > 0:
            logger.info(f"Loaded existing collection '{collection_name}' with {count} vectors")
            return existing

        # Collection is empty and we have documents – populate it
        if documents:
            chunks = chunk_documents(documents)
            logger.info(f"Creating new collection '{collection_name}' from {len(chunks)} chunks")
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=persist_dir,
            )
            logger.info(f"Collection '{collection_name}' created and persisted")
            return vector_store

        raise VectorStoreError(f"No existing index and no documents provided for song_id={song_id}")

    except VectorStoreError:
        raise
    except Exception as e:
        logger.error(f"Vector store operation failed: {e}")
        raise VectorStoreError(detail=str(e))


def get_retriever(song_id: str, k: int = RETRIEVER_K) -> VectorStoreRetriever:
    """
    Get a retriever for an existing song's vector collection.

    Args:
        song_id: The song to retrieve vectors for.
        k: Number of chunks to retrieve per query.

    Returns:
        A VectorStoreRetriever ready for RAG queries.
    """
    vector_store = create_or_load_index(song_id)
    return vector_store.as_retriever(search_kwargs={"k": k})
