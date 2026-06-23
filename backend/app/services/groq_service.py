"""
Groq LLM service.

Factory for ChatGroq instances using application settings.
Single responsibility: produce configured LLM objects.
"""

from langchain_groq import ChatGroq

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger("services.groq")


def get_llm(temperature: float | None = None) -> ChatGroq:
    """
    Create a configured ChatGroq instance.

    Args:
        temperature: Override the default temperature from settings.

    Returns:
        A ready-to-use ChatGroq LLM.
    """
    settings = get_settings()
    temp = temperature if temperature is not None else settings.GROQ_TEMPERATURE

    logger.info(f"Initializing ChatGroq model={settings.GROQ_MODEL} temp={temp}")
    return ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=temp,
        api_key=settings.GROQ_API_KEY,
    )
