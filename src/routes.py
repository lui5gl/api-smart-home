"""API route definitions for the simplified Smart Home service."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .security import require_skill_token
from .services import DeviceService, HealthService


router = APIRouter()
health_service = HealthService()
device_service = DeviceService()
skill_token_dependency = Depends(require_skill_token)


class DeviceStatePayload(BaseModel):
    device_uuid: str
    status: bool


class DeviceCreatePayload(BaseModel):
    status: bool | None = False


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    return health_service.check_database()


@router.get("/devices", dependencies=[skill_token_dependency])
def list_device_states() -> list[dict[str, Any]]:
    return device_service.list_device_states()


@router.get("/devices/{device_uuid}", dependencies=[skill_token_dependency])
def get_device_state(device_uuid: str) -> dict[str, Any]:
    return device_service.get_device_state(device_uuid)


@router.post("/devices", dependencies=[skill_token_dependency])
def create_device_state(payload: DeviceCreatePayload | None = None) -> dict[str, Any]:
    desired_status = payload.status if payload and payload.status is not None else False
    return device_service.create_device_state(desired_status)


@router.post("/devices/state", dependencies=[skill_token_dependency])
def set_device_state(payload: DeviceStatePayload) -> dict[str, Any]:
    return device_service.set_device_state(
        device_uuid=payload.device_uuid,
        status=payload.status,
    )
