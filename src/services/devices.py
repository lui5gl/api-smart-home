"""File-based device state management."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DeviceService:
    """Persist a single boolean device state using a JSON file."""

    def __init__(self, state_path: str | Path | None = None) -> None:
        base_path = Path(__file__).resolve().parents[2]
        configured_path = os.getenv("STATE_FILE_PATH")
        self._state_path = Path(state_path or configured_path or base_path / "device_state.json")

    def get_state(self) -> dict[str, str]:
        """Return the device state as a human-readable payload."""
        return self._format_response(self._read_state())

    def set_state(self, status: bool) -> dict[str, str]:
        """Persist a new state and return the updated snapshot."""
        return self._format_response(self._write_state(status))

    def toggle_state(self) -> dict[str, str]:
        """Invert the stored state."""
        current = self._read_state()
        return self._format_response(self._write_state(not current["status"]))

    def _read_state(self) -> dict[str, Any]:
        if not self._state_path.exists():
            return {"status": False, "last_updated": None}

        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"status": False, "last_updated": None}

        return {
            "status": bool(data.get("status", False)),
            "last_updated": data.get("last_updated"),
        }

    def _write_state(self, status: bool) -> dict[str, Any]:
        payload = {
            "status": bool(status),
            "last_updated": datetime.now(tz=timezone.utc).isoformat(),
        }
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(payload), encoding="utf-8")
        return payload

    @staticmethod
    def _format_response(state: dict[str, Any]) -> dict[str, str]:
        return {
            "status": "on" if state["status"] else "off",
            "last_updated": state.get("last_updated"),
        }
