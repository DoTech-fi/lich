"""
Health check endpoints.
"""
from fastapi import APIRouter
from internal.dto.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check."""
    return HealthResponse(
        status="healthy",
        service="{{ cookiecutter.project_slug }}-api",
        version="1.0.0",
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check - verify all dependencies are available."""
    # TODO: Add database/cache connectivity checks
    return HealthResponse(
        status="ready",
        service="{{ cookiecutter.project_slug }}-api",
        version="1.0.0",
    )
