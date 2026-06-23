"""
Health check endpoint.

Provides system health status including connectivity
to Neo4j and vector store availability.
"""

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from app.config.settings import get_settings
from app.database.neo4j import get_neo4j_session
from app.schemas.responses import HealthResponse, ServiceStatus
from app.utils.logger import get_logger

logger = get_logger("api.health")
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Returns the health status of the Sonus API and its dependencies.",
)
async def health_check(
    neo4j_session: AsyncSession = Depends(get_neo4j_session),
) -> HealthResponse:
    """Check connectivity to Neo4j and report overall system health."""
    settings = get_settings()
    services = ServiceStatus()

    # Check Neo4j
    try:
        result = await neo4j_session.run("RETURN 1 AS ping")
        await result.single()
        services.neo4j = "healthy"
    except Exception as e:
        logger.warning(f"Neo4j health check failed: {e}")
        services.neo4j = f"unhealthy: {e}"

    # Check vector store directory
    from pathlib import Path

    chroma_dir = Path(settings.CHROMA_PERSIST_DIR)
    services.vector_store = "healthy" if chroma_dir.exists() else "not_initialized"

    overall = "ok" if services.neo4j == "healthy" else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        services=services,
    )
