from fastapi import FastAPI

from app.api.routes import health
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to Ethara API"}
