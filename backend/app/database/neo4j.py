"""
Neo4j async driver lifecycle management.

Provides a singleton AsyncDriver initialized during FastAPI lifespan
and a dependency function for per-request AsyncSession injection.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from app.config.settings import get_settings
from app.utils.logger import get_logger
from app.utils.exceptions import Neo4jConnectionError

logger = get_logger("database.neo4j")

# Module-level driver reference – set during lifespan startup
_driver: AsyncDriver | None = None


async def init_driver() -> AsyncDriver:
    """Create and verify the Neo4j async driver. Call once at startup."""
    global _driver
    settings = get_settings()

    try:
        _driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        # Verify connectivity against the target database
        await _driver.verify_connectivity()
        logger.info("Neo4j driver initialized and connectivity verified")
        return _driver
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j driver: {e}")
        raise Neo4jConnectionError(detail=str(e))


async def close_driver() -> None:
    """Close the Neo4j driver. Call once at shutdown."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")


def get_driver() -> AsyncDriver:
    """Return the active driver instance. Raises if not initialized."""
    if _driver is None:
        raise Neo4jConnectionError(detail="Neo4j driver not initialized")
    return _driver


async def get_neo4j_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession scoped to the request.

    Usage in route:
        async def my_route(session=Depends(get_neo4j_session)):
            ...
    """
    driver = get_driver()
    settings = get_settings()
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        yield session
