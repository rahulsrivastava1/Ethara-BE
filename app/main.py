from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes import customers, health, orders, products
from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to Ethara API"}
