"""Database seeding helpers."""

from __future__ import annotations

from typing import Iterable

from .database import Database


class DatabaseSeeder:
    """Executes SQL statements to bootstrap baseline data."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def reset_schema(self) -> None:
        """Drop managed tables. Intended for development use."""
        self._execute_statements(
            [
                "DROP TABLE IF EXISTS device_states CASCADE;",
            ]
        )

    def _execute_statements(self, statements: Iterable[str]) -> None:
        with self._db.cursor() as cur:
            for statement in statements:
                cur.execute(statement)

    def seed_device_states(self) -> None:
        setup_statements = [
            """
            CREATE TABLE IF NOT EXISTS device_states (
                device_uuid UUID PRIMARY KEY,
                status BOOLEAN NOT NULL DEFAULT FALSE,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """,
        ]

        self._execute_statements(setup_statements)

    def run_all(self) -> dict[str, str]:
        self.seed_device_states()
        return {"status": "seeded"}
