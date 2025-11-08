"""API route definitions for the Smart Home service."""

from fastapi import APIRouter
from pydantic import BaseModel

from .services import DeviceService, HealthService


router = APIRouter()
health_service = HealthService()
device_service = DeviceService()


class DeviceStatusPayload(BaseModel):
    username: str
    device_name: str
    status: bool


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    return health_service.check_database()


@router.post("/devices/status")
def update_device_status(payload: DeviceStatusPayload) -> dict[str, str]:
    return device_service.update_status(
        username=payload.username,
        device_name=payload.device_name,
        status=payload.status,
    )
