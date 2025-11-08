"""Password hashing helpers."""

from passlib.context import CryptContext

_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _PWD_CONTEXT.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _PWD_CONTEXT.verify(password, hashed_password)
