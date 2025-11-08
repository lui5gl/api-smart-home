"""Database helpers for the Smart Home API."""

import os
from contextlib import contextmanager

import psycopg


class Database:
    """Simple helper to build PostgreSQL connections from environment variables."""

    def __init__(self) -> None:
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.dbname = os.getenv("POSTGRES_DB", "postgres")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")

    def connect(self) -> psycopg.Connection:
        return psycopg.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    @contextmanager
    def cursor(self) -> psycopg.Cursor:
        with self.connect() as connection:
            with connection.cursor() as cur:
                yield cur
                connection.commit()
