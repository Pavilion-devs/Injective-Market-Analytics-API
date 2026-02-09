"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from config import settings
from models import HealthStatus
from services import injective_service

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Check API health status
    
    Returns basic information about the API status and configuration.
    """
    return HealthStatus(
        status="healthy",
        version=settings.api_version,
        network=settings.network,
        timestamp=datetime.utcnow().isoformat(),
        cache_size=len(injective_service._cache),
    )


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear the API cache
    
    Useful for forcing fresh data retrieval from Injective network.
    """
    injective_service.clear_cache()
    return {
        "status": "success",
        "message": "Cache cleared",
        "timestamp": datetime.utcnow().isoformat(),
    }
