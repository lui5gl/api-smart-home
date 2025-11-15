import logging

from fastapi import FastAPI

from .config import ensure_env_file
from .routes import router


env_creation = ensure_env_file()

if env_creation.get("created"):
    logging.getLogger(__name__).warning(
        "Created new environment file at %s. Keep it safe!",
        env_creation.get("path"),
    )


app = FastAPI(title="Smart Home API")
app.include_router(router)
