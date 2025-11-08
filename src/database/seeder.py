"""Database seeding helpers."""

from __future__ import annotations

from typing import Iterable

from .database import Database


class DatabaseSeeder:
    """Executes SQL statements to bootstrap baseline data."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def _execute_statements(self, statements: Iterable[str]) -> None:
        with self._db.cursor() as cur:
            for statement in statements:
                cur.execute(statement)

    def seed_devices(self) -> None:
        setup_statements = [
            """
            CREATE TABLE IF NOT EXISTS devices (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                status BOOLEAN NOT NULL DEFAULT FALSE
            );
            """
        ]

        self._execute_statements(setup_statements)

        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO devices (name, status)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING;
                """,
                ("Thermostat", True),
            )

    def run_all(self) -> dict[str, str]:
        self.seed_devices()
        return {"status": "seeded"}
