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


class DeviceTogglePayload(BaseModel):
    device_uuid: str


class DeviceCreatePayload(BaseModel):
    status: bool | None = False


@router.get("/health")
def health_check() -> dict[str, str]:
    """
    Report the service readiness status.

    params: none
    return: dict with overall API readiness status
    """
    return {"status": "ok"}


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    """
    Check connectivity with the backing database.

    params: none
    return: dict describing database connectivity status and message
    """
    return health_service.check_database()


@router.get("/devices", dependencies=[skill_token_dependency])
def list_device_states() -> list[dict[str, Any]]:
    """
    List all devices the service currently tracks.

    params: none
    return: list of device dicts, each containing metadata and state
    """
    return device_service.list_device_states()


@router.get("/device-status", dependencies=[skill_token_dependency])
def get_device_state_query(device_uuid: str) -> dict[str, Any]:
    """
    Retrieve a device state via query parameter.

    params: query param device_uuid (str)
    return: dict containing the requested device state
    """
    return device_service.get_device_state(device_uuid)


@router.get("/devices/{device_uuid}", dependencies=[skill_token_dependency])
def get_device_state(device_uuid: str) -> dict[str, Any]:
    """
    Retrieve a device state via path parameter.

    params: path param device_uuid (str)
    return: dict containing the requested device state
    """
    return device_service.get_device_state(device_uuid)


@router.post("/devices", dependencies=[skill_token_dependency])
def create_device_state(payload: DeviceCreatePayload | None = None) -> dict[str, Any]:
    """
    Create a new device with an optional initial state.

    params: optional JSON payload with field status (bool)
    return: dict describing the newly created device and its state
    """
    desired_status = payload.status if payload and payload.status is not None else False
    return device_service.create_device_state(desired_status)


@router.post("/devices/state", dependencies=[skill_token_dependency])
def set_device_state(payload: DeviceStatePayload) -> dict[str, Any]:
    """
    Force a device into a specific state.

    params: JSON payload with device_uuid (str) and status (bool)
    return: dict describing the updated device state
    """
    return device_service.set_device_state(
        device_uuid=payload.device_uuid,
        status=payload.status,
    )


@router.post("/devices/toggle", dependencies=[skill_token_dependency])
def toggle_device_state(payload: DeviceTogglePayload) -> dict[str, Any]:
    """
    Toggle the state of a device without caring about its current value.

    params: JSON payload with device_uuid (str)
    return: dict describing the device after toggling its state
    """
    return device_service.toggle_device_state(payload.device_uuid)
