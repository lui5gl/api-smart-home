"""API route definitions for the Smart Home service."""

from fastapi import APIRouter

from .services import HealthService


router = APIRouter()
health_service = HealthService()


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    return health_service.check_database()
