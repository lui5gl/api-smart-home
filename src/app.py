from fastapi import FastAPI

from .routes import router
from .services import SeedService


app = FastAPI(title="Smart Home API")
seed_service = SeedService()


@app.on_event("startup")
def seed_database() -> None:
    seed_service.seed_database()


app.include_router(router)
