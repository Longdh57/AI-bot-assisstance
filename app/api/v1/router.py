from fastapi import APIRouter

from app.api.v1.endpoints.cards import router as cards_router
from app.api.v1.endpoints.current_lists import router as current_lists_router

api_router = APIRouter()

api_router.include_router(cards_router, prefix="/cards", tags=["cards"])
api_router.include_router(current_lists_router, prefix="/current-lists", tags=["current-lists"])
