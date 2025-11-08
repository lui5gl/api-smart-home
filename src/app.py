import logging

from fastapi import FastAPI

from .config import ensure_env_file
from .routes import router
from .services import SeedService


env_creation = ensure_env_file()

if env_creation.get("created"):
    logging.getLogger(__name__).warning(
        "Created new environment file at %s. Keep it safe!",
        env_creation.get("path"),
    )


app = FastAPI(title="Smart Home API")
seed_service = SeedService()


@app.on_event("startup")
def seed_database() -> None:
    seed_service.seed_database()


app.include_router(router)
