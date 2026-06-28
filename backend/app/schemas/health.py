from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    neo4j: str = "unknown"


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = ""
    services: ServiceStatus = Field(default_factory=ServiceStatus)
