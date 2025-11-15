"""Business logic for the Alexa-triggered device state."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from ..database import Database


class DeviceService:
    """Store and toggle smart-home device state keyed by UUID."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def list_device_states(self) -> list[dict[str, Any]]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT device_uuid, status, updated_at
                FROM device_states
                ORDER BY updated_at DESC;
                """
            )
            rows = cur.fetchall()

        return [self._serialize_row(row) for row in rows]

    def create_device_state(self, status: bool) -> dict[str, Any]:
        device_uuid = uuid4()
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO device_states (device_uuid, status)
                VALUES (%s, %s)
                RETURNING device_uuid, status, updated_at;
                """,
                (device_uuid, status),
            )
            row = cur.fetchone()

        return self._serialize_row(row)

    def get_device_state(self, device_uuid: str) -> dict[str, Any]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT device_uuid, status, updated_at
                FROM device_states
                WHERE device_uuid = %s;
                """,
                (device_uuid,),
            )
            row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Device not registered")

        return self._serialize_row(row)

    def toggle_device_state(self, device_uuid: str) -> dict[str, Any]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT status
                FROM device_states
                WHERE device_uuid = %s;
                """,
                (device_uuid,),
            )
            row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Device not registered")

        current_status = bool(row[0])
        return self.set_device_state(device_uuid=device_uuid, status=not current_status)

    def set_device_state(self, device_uuid: str, status: bool) -> dict[str, Any]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO device_states (device_uuid, status)
                VALUES (%s, %s)
                ON CONFLICT (device_uuid) DO UPDATE
                    SET status = EXCLUDED.status,
                        updated_at = NOW()
                RETURNING device_uuid, status, updated_at;
                """,
                (device_uuid, status),
            )
            row = cur.fetchone()

        return self._serialize_row(row)

    @staticmethod
    def _serialize_row(row: tuple[Any, ...]) -> dict[str, Any]:
        device_uuid, status, updated_at = row
        return {
            "device_uuid": str(device_uuid),
            "status": "on" if status else "off",
            "last_updated": DeviceService._format_datetime(updated_at),
        }

    @staticmethod
    def _format_datetime(value: Any) -> str | None:
        if isinstance(value, datetime):
            return value.isoformat()
        return None
