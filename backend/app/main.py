"""
Sonus API — FastAPI Application Entry Point

Production-grade cultural song analysis & interpretation engine.

Lifecycle:
  - Startup:  Initialize Neo4j driver, run constraints, create vector index, set up logging.
  - Shutdown: Close Neo4j driver gracefully.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, rag, songs, transcript, translation
from app.config.settings import get_settings
from app.database.neo4j import close_driver, get_neo4j_session, init_driver
from app.middleware.request_logger import RequestLoggerMiddleware
from app.services import neo4j_service
from app.utils.exceptions import SonusException, sonus_exception_handler
from app.utils.logger import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
      1. Configure structured logging
      2. Initialize Neo4j driver and verify connectivity
      3. Run database constraints
      4. Create vector index on Chunk.embedding
      5. Create BM25 full-text index on Chunk.content
    Shutdown:
      1. Close Neo4j driver
    """
    # ── Startup ──────────────────────────────────────────────────
    setup_logging()
    logger = get_logger("app")
    settings = get_settings()

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize Neo4j
    driver = await init_driver()

    # Run constraints and indexes (idempotent -- IF NOT EXISTS)
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        await neo4j_service.setup_constraints(session)
        await neo4j_service.setup_vector_index(session)
        await neo4j_service.setup_bm25_index(session)

    logger.info("Application startup complete")

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("Shutting down application")
    await close_driver()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Application factory — builds and configures the FastAPI app."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "🎵 **Sonus** — A production-grade cultural song analysis & interpretation engine.\n\n"
            "Powered by Groq LLM, HuggingFace embeddings, and Neo4j — a unified graph database "
            "that stores song relationships, lyrics, translations, and vector embeddings "
            "in a single consistent store.\n\n"
            "## Features\n"
            "- **Song Ingestion** — YouTube metadata, transcript extraction with ElevenLabs fallback\n"
            "- **Cultural Interpretation** — Ethnomusicologist-level lyric analysis via RAG\n"
            "- **Literary Translation** — Poetic localization preserving artistic intent\n"
            "- **Knowledge Graph** — Neo4j-backed song, artist, genre, and theme relationships\n"
            "- **Native Vector Search** — Neo4j vector index with exact KNN for per-song RAG\n"
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Middleware ────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggerMiddleware)

    # ── Exception Handlers ───────────────────────────────────────
    app.add_exception_handler(SonusException, sonus_exception_handler)

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(health.router, prefix="/api")
    app.include_router(songs.router, prefix="/api")
    app.include_router(transcript.router, prefix="/api")
    app.include_router(translation.router, prefix="/api")
    app.include_router(rag.router, prefix="/api")

    return app


# The app instance used by uvicorn
app = create_app()

import uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 