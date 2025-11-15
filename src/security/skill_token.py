"""Helpers to validate Alexa skill requests."""

import os

from fastapi import Header, HTTPException


def require_skill_token(x_skill_token: str = Header(..., alias="X-Skill-Token")) -> None:
    """Ensure the incoming request is authorized by Alexa/Arduino."""

    expected = os.getenv("ALEXA_SKILL_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=500,
            detail="Skill token is not configured",
        )

    if not x_skill_token or x_skill_token != expected:
        raise HTTPException(status_code=401, detail="Invalid skill token")
