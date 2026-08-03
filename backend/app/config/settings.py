"""
Application settings loaded from environment variables.

Uses pydantic-settings to validate and parse all configuration
from .env files and system environment with type safety.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Sonus backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── LLM Provider ──────────────────────────────────────────────
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.3

    # ── Embeddings ────────────────────────────────────────────────
    # all-MiniLM-L6-v2 produces 384-dimensional dense vectors.
    # Changing this model requires recreating the Neo4j vector index.
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── ElevenLabs (Speech-to-Text Fallback) ──────────────────────
    ELEVENLABS_API_KEY: str = ""

    # ── Hugging Face ──────────────────────────────────────────────
    # If provided, uses Hugging Face Serverless Inference API for embeddings (saves RAM)
    HF_TOKEN: str = ""

    # ── Neo4j ─────────────────────────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "sonus_password"
    NEO4J_DATABASE: str = "sonus"

    # ── Application ───────────────────────────────────────────────
    APP_NAME: str = "Sonus API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Production-grade cultural song analysis & interpretation engine"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton – parsed once, reused everywhere."""
    return Settings()
