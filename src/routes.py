"""API route definitions for the simplified Smart Home service."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .security import require_skill_token
from .services import DeviceService


router = APIRouter()
device_service = DeviceService()
skill_token_dependency = Depends(require_skill_token)


class DeviceStatePayload(BaseModel):
    status: bool


@router.get("/health")
def health_check() -> dict[str, str]:
    """Report the service readiness status."""
    return {"status": "ok"}


@router.get("/device-status", dependencies=[skill_token_dependency])
def get_device_state() -> dict[str, str]:
    """Retrieve the current device state."""
    return device_service.get_state()


@router.post("/device-status", dependencies=[skill_token_dependency])
def set_device_state(payload: DeviceStatePayload) -> dict[str, str]:
    """Force the device into a specific state."""
    return device_service.set_state(status=payload.status)


@router.post("/device-status/toggle", dependencies=[skill_token_dependency])
def toggle_device_state() -> dict[str, str]:
    """Toggle the device state without providing a value."""
    return device_service.toggle_state()
