"""Database seeding helpers."""

from __future__ import annotations

from typing import Iterable

from .database import Database


class DatabaseSeeder:
    """Executes SQL statements to bootstrap baseline data."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def reset_schema(self) -> None:
        """Drop all managed tables. Intended for development use."""
        drop_statements = [
            "DROP TABLE IF EXISTS account_devices CASCADE;",
            "DROP TABLE IF EXISTS devices CASCADE;",
            "DROP TABLE IF EXISTS users CASCADE;",
        ]
        self._execute_statements(drop_statements)

    def _execute_statements(self, statements: Iterable[str]) -> None:
        with self._db.cursor() as cur:
            for statement in statements:
                cur.execute(statement)

    def seed_devices(self) -> None:
        setup_statements = [
            'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',
            """
            CREATE TABLE IF NOT EXISTS devices (
                id SERIAL PRIMARY KEY,
                device_uuid UUID NOT NULL DEFAULT gen_random_uuid(),
                name TEXT UNIQUE NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """,
            """
            ALTER TABLE devices
            ADD COLUMN IF NOT EXISTS device_uuid UUID;
            """,
            """
            UPDATE devices
            SET device_uuid = gen_random_uuid()
            WHERE device_uuid IS NULL;
            """,
            """
            ALTER TABLE devices
            ALTER COLUMN device_uuid SET DEFAULT gen_random_uuid();
            """,
            """
            ALTER TABLE devices
            ALTER COLUMN device_uuid SET NOT NULL;
            """,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'uq_devices_device_uuid'
                ) THEN
                    ALTER TABLE devices
                    ADD CONSTRAINT uq_devices_device_uuid UNIQUE (device_uuid);
                END IF;
            END;
            $$;
            """,
        ]

        self._execute_statements(setup_statements)

        # No default device row inserted to avoid seeding fake data.

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

        # Do not insert default users in production environments.

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

        # Associations are left for real user actions.
