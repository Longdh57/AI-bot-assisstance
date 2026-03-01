from fastapi import APIRouter

from app.api.v1.endpoints.cards import router as cards_router

api_router = APIRouter()

api_router.include_router(cards_router, prefix="/cards", tags=["cards"])
