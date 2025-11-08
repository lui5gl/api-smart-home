from fastapi import FastAPI

from .routes import router


app = FastAPI(title="Smart Home API")
app.include_router(router)
