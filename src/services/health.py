"""Health-check related services."""

import psycopg
from fastapi import HTTPException

from ..database import Database


class HealthService:
    """Encapsulates health-check logic so routes remain thin."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def check_database(self) -> dict[str, str]:
        try:
            with self._db.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            return {"status": "ok"}
        except psycopg.Error as exc:
            raise HTTPException(
                status_code=500, detail="Database connection failed"
            ) from exc
