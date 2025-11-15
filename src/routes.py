"""API route definitions for the Smart Home service."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .security import require_skill_token
from .services import DeviceService, HealthService, UserService


router = APIRouter()
health_service = HealthService()
device_service = DeviceService()
user_service = UserService()
skill_token_dependency = Depends(require_skill_token)


class DeviceStatusPayload(BaseModel):
    username: str
    device_uuid: str
    status: bool


class DeviceRenamePayload(BaseModel):
    username: str
    device_uuid: str
    new_name: str


class DeviceCreatePayload(BaseModel):
    username: str
    device_name: str
    serial_number: str
    status: bool | None = False


class UserRegistrationPayload(BaseModel):
    name: str
    username: str
    password: str


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    return health_service.check_database()


@router.get("/devices", dependencies=[skill_token_dependency])
def list_user_devices(username: str) -> list[dict[str, Any]]:
    return device_service.list_user_devices(username)


@router.get("/devices/status", dependencies=[skill_token_dependency])
def get_device_status(username: str, device_uuid: str) -> dict[str, Any]:
    return device_service.get_device_status(username, device_uuid)


@router.post("/devices/status", dependencies=[skill_token_dependency])
def update_device_status(payload: DeviceStatusPayload) -> dict[str, str]:
    return device_service.update_status(
        username=payload.username,
        device_uuid=payload.device_uuid,
        status=payload.status,
    )


@router.patch("/devices/name", dependencies=[skill_token_dependency])
def rename_device(payload: DeviceRenamePayload) -> dict[str, str]:
    return device_service.rename_device(
        username=payload.username,
        device_uuid=payload.device_uuid,
        new_name=payload.new_name,
    )


@router.post("/devices", dependencies=[skill_token_dependency])
def add_device(payload: DeviceCreatePayload) -> dict[str, str]:
    return device_service.add_device(
        username=payload.username,
        device_name=payload.device_name,
        serial_number=payload.serial_number,
        status=payload.status if payload.status is not None else False,
    )


@router.post("/users/register")
def register_user(payload: UserRegistrationPayload) -> dict[str, str]:
    return user_service.register(
        name=payload.name,
        username=payload.username,
        password=payload.password,
    )
