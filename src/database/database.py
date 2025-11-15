"""Database helpers for the Smart Home API."""

import os
from contextlib import contextmanager

import psycopg
from psycopg import sql


class Database:
    """Simple helper to build PostgreSQL connections from environment variables."""

    def __init__(self) -> None:
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.dbname = os.getenv("POSTGRES_DB", "postgres")
        self.default_db = os.getenv("POSTGRES_DEFAULT_DB", "postgres")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")

    def connect(self) -> psycopg.Connection:
        try:
            return psycopg.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )
        except psycopg.OperationalError as exc:
            if "does not exist" in str(exc):
                self._create_database()
                return psycopg.connect(
                    host=self.host,
                    port=self.port,
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                )
            raise

    @contextmanager
    def cursor(self) -> psycopg.Cursor:
        with self.connect() as connection:
            with connection.cursor() as cur:
                yield cur
                connection.commit()

    def _create_database(self) -> None:
        with psycopg.connect(
            host=self.host,
            port=self.port,
            dbname=self.default_db,
            user=self.user,
            password=self.password,
        ) as connection:
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (self.dbname,),
                )
                if cur.fetchone():
                    return
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname))
                )
                connection.commit()
