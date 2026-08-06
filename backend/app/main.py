"""
Sonus API — FastAPI Application Entry Point

Production-grade cultural song analysis & interpretation engine.

Lifecycle:
  - Startup:  Generate cookie file, initialize Neo4j driver, run constraints, create vector index, set up logging.
  - Shutdown: Close Neo4j driver gracefully.
"""

from contextlib import asynccontextmanager
import os
import base64
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp.version import __version__ as YTDLP_VERSION

from app.api import health, rag, songs, transcript, translation
from app.config.settings import get_settings
from app.database.neo4j import close_driver, get_neo4j_session, init_driver
from app.middleware.request_logger import RequestLoggerMiddleware
from app.services import neo4j_service
from app.utils.exceptions import SonusException, sonus_exception_handler
from app.utils.logger import get_logger, setup_logging


def setup_youtube_cookies(logger):
    """Recreates youtube_cookies.txt at runtime from YOUTUBE_COOKIES_BASE64 env var.

    Validates the decoded content is non-trivial before writing, so a bad/stale
    env var fails loudly at startup instead of silently producing a useless
    cookie file that services then quietly ignore (or worse, pass to yt-dlp
    and get a confusing downstream error).
    """
    # Resolves to root folder: app/main.py -> app/ -> root/
    cookie_path = Path(__file__).resolve().parent.parent / "youtube_cookies.txt"
    cookie_env = os.getenv("YOUTUBE_COOKIES_BASE64")

    if not cookie_env:
        logger.warning(
            "YOUTUBE_COOKIES_BASE64 not found in environment variables. "
            "Proceeding without cookies — some videos may fail to extract."
        )
        return

    try:
        decoded_cookies = base64.b64decode(cookie_env).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decode YOUTUBE_COOKIES_BASE64 environment variable: {e}")
        return

    if "youtube.com" not in decoded_cookies or len(decoded_cookies.strip()) < 20:
        logger.error(
            "Decoded YOUTUBE_COOKIES_BASE64 does not look like a valid Netscape "
            "cookies.txt file (missing 'youtube.com' or too short). Refusing to "
            "write it — check the env var was exported correctly and is current."
        )
        return

    try:
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(decoded_cookies)
        logger.info(
            f"Successfully generated youtube_cookies.txt "
            f"({len(decoded_cookies)} bytes) from environment variable."
        )
    except Exception as e:
        logger.error(f"Failed to write youtube_cookies.txt to {cookie_path}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    """
    # ── Startup ──────────────────────────────────────────────────
    setup_logging()
    logger = get_logger("app")
    settings = get_settings()

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Using yt-dlp version {YTDLP_VERSION}")

    # 1. Setup cookies BEFORE services try to use them!
    setup_youtube_cookies(logger)

    # 2. Initialize Neo4j
    driver = await init_driver()

    # Run constraints and indexes (idempotent -- IF NOT EXISTS)
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        await neo4j_service.setup_constraints(session)
        await neo4j_service.setup_vector_index(session)
        await neo4j_service.setup_bm25_index(session)

    logger.info("Application startup complete")

    yield  # Application runs while suspended here

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)