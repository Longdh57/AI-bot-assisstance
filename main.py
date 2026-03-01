from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.database import AsyncSessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify MySQL connection
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("MySQL connection established.")
    yield
    # Shutdown: dispose engine
    await engine.dispose()
    print("MySQL connection closed.")


app = FastAPI(
    title="Trello Reminder",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health check endpoint."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
