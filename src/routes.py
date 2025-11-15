"""API route definitions for the simplified Smart Home service."""

from fastapi import APIRouter
from pydantic import BaseModel

from .services import DeviceService


router = APIRouter()
device_service = DeviceService()


class DeviceStatePayload(BaseModel):
    status: bool


@router.get("/health")
def health_check() -> dict[str, str]:
    """Report the service readiness status."""
    return {"status": "ok"}


@router.get("/device-status")
def get_device_state() -> dict[str, str | None]:
    """Retrieve the current device state."""
    return device_service.get_state()


@router.post("/device-status")
def set_device_state(payload: DeviceStatePayload) -> dict[str, str | None]:
    """Force the device into a specific state."""
    return device_service.set_state(status=payload.status)


@router.post("/device-status/toggle")
def toggle_device_state() -> dict[str, str | None]:
    """Toggle the device state without providing a value."""
    return device_service.toggle_state()
