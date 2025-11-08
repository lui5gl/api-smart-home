"""Service layer for user-related operations."""

from fastapi import HTTPException

from ..database import Database
from ..security import hash_password


class UserService:
    """Handle account creation logic."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()

    def register(self, name: str, username: str, password: str) -> dict[str, str]:
        hashed_password = hash_password(password)

        with self._db.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE username = %s",
                (username,),
            )
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already taken")

            cur.execute(
                """
                INSERT INTO users (name, username, password, last_entry)
                VALUES (%s, %s, %s, NOW())
                RETURNING id;
                """,
                (name, username, hashed_password),
            )
            user_id = cur.fetchone()[0]

        return {"id": str(user_id), "username": username}
