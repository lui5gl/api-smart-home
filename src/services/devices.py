"""Business logic for interacting with smart devices."""

from fastapi import HTTPException

from ..database import Database


class DeviceService:
    """Provide helpers to mutate device state for a specific account."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def update_status(self, username: str, device_name: str, status: bool) -> dict[str, str]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT ad.id
                FROM account_devices ad
                JOIN users u ON ad.user_id = u.id
                JOIN devices d ON ad.device_id = d.id
                WHERE u.username = %s AND d.name = %s;
                """,
                (username, device_name),
            )
            account_device = cur.fetchone()

            if not account_device:
                raise HTTPException(
                    status_code=404,
                    detail="Device not associated with this account",
                )

            account_device_id = account_device[0]

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
