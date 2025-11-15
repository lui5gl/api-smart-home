"""Utilities to ensure environment configuration exists."""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Dict


def ensure_env_file(env_path: str | Path | None = None) -> Dict[str, str | bool]:
    """Create a .env file with secure defaults if it does not exist."""

    project_root = Path(__file__).resolve().parents[2]
    target_path = Path(env_path) if env_path else project_root / ".env"

    if target_path.exists():
        return {"created": False, "path": str(target_path)}

    target_path.parent.mkdir(parents=True, exist_ok=True)

    secrets_map = {
        "ENV": "production",
        "POSTGRES_HOST": "smart-home-db",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "smart_home",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": _generate_secret(),
        "ADMIN_NAME": "Administrator",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": _generate_secret(),
        "ALEXA_SKILL_TOKEN": _generate_secret(),
    }

    lines = ["# Auto-generated configuration\n"]
    lines.extend(f"{key}={value}\n" for key, value in secrets_map.items())

    target_path.write_text("".join(lines), encoding="utf-8")

    return {
        "created": True,
        "path": str(target_path),
        "admin_password": secrets_map["ADMIN_PASSWORD"],
        "postgres_password": secrets_map["POSTGRES_PASSWORD"],
    }


def _generate_secret() -> str:
    return secrets.token_urlsafe(24)
