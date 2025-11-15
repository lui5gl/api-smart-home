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
        "STATE_FILE_PATH": str(project_root / "device_state.json"),
    }

    lines = ["# Auto-generated configuration\n"]
    lines.extend(f"{key}={value}\n" for key, value in secrets_map.items())

    target_path.write_text("".join(lines), encoding="utf-8")

    return {
        "created": True,
        "path": str(target_path),
        "state_file": secrets_map["STATE_FILE_PATH"],
    }


def _generate_secret() -> str:
    return secrets.token_urlsafe(24)
