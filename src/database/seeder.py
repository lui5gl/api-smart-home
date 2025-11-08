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
                serial_number TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ]

        self._execute_statements(setup_statements)

        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO devices (name, serial_number)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING;
                """,
                ("Thermostat", "THERMO-001"),
            )

    def seed_users(self) -> None:
        setup_statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                last_entry TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ]

        self._execute_statements(setup_statements)

        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (name, username, password, last_entry)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (username) DO NOTHING;
                """,
                ("Admin", "admin", "changeme"),
            )

    def run_all(self) -> dict[str, str]:
        self.seed_devices()
        self.seed_users()
        self.seed_account_devices()
        return {"status": "seeded"}

    def seed_account_devices(self) -> None:
        setup_statements = [
            """
            CREATE TABLE IF NOT EXISTS account_devices (
                id SERIAL PRIMARY KEY,
                device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                status BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (device_id, user_id)
            );
            """
        ]

        self._execute_statements(setup_statements)

        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO account_devices (device_id, user_id, status)
                VALUES (
                    (SELECT id FROM devices WHERE name = %s),
                    (SELECT id FROM users WHERE username = %s),
                    %s
                )
                ON CONFLICT (device_id, user_id) DO NOTHING;
                """,
                ("Thermostat", "admin", True),
            )
