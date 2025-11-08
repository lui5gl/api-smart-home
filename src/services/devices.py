"""Business logic for interacting with smart devices."""

from datetime import datetime
from typing import Any

import psycopg
from fastapi import HTTPException

from ..database import Database


class DeviceService:
    """Provide helpers to mutate device state for a specific account."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def update_status(self, username: str, device_name: str, status: bool) -> dict[str, str]:
        account_device_id, _ = self._get_device_association(username, device_name)

        with self._db.cursor() as cur:
            cur.execute(
                """
                UPDATE account_devices
                SET status = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING status;
                """,
                (status, account_device_id),
            )
            updated_status = cur.fetchone()

        state = "on" if updated_status and updated_status[0] else "off"
        return {"device": device_name, "status": state}

    def list_user_devices(self, username: str) -> list[dict[str, Any]]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT d.name, d.serial_number, ad.status, ad.updated_at
                FROM account_devices ad
                JOIN users u ON ad.user_id = u.id
                JOIN devices d ON ad.device_id = d.id
                WHERE u.username = %s
                ORDER BY d.name;
                """,
                (username,),
            )
            rows = cur.fetchall()

        devices: list[dict[str, Any]] = []
        for name, serial_number, status, updated_at in rows:
            devices.append(
                {
                    "name": name,
                    "serial_number": serial_number,
                    "status": "on" if status else "off",
                    "last_updated": self._format_datetime(updated_at),
                }
            )

        return devices

    def rename_device(self, username: str, current_name: str, new_name: str) -> dict[str, str]:
        _, device_id = self._get_device_association(username, current_name)

        with self._db.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE devices
                    SET name = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING name;
                    """,
                    (new_name, device_id),
                )
                updated = cur.fetchone()
            except psycopg.errors.UniqueViolation as exc:
                raise HTTPException(
                    status_code=400, detail="Device name already in use"
                ) from exc

        return {"device": updated[0], "status": "renamed"}

    def _get_device_association(self, username: str, device_name: str) -> tuple[int, int]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT ad.id, d.id
                FROM account_devices ad
                JOIN users u ON ad.user_id = u.id
                JOIN devices d ON ad.device_id = d.id
                WHERE u.username = %s AND d.name = %s;
                """,
                (username, device_name),
            )
            result = cur.fetchone()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Device not associated with this account",
            )

        return int(result[0]), int(result[1])

    @staticmethod
    def _format_datetime(value: Any) -> str | None:
        if isinstance(value, datetime):
            return value.isoformat()
        return None
