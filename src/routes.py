"""API route definitions for the Smart Home service."""

from fastapi import APIRouter

from .services import HealthService, SeedService


router = APIRouter()
health_service = HealthService()
seed_service = SeedService()


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    return health_service.check_database()


@router.post("/database/seed")
def seed_database() -> dict[str, str]:
    return seed_service.seed_database()
