from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.services.card_service import CardService
from app.services.trello_client import TrelloClient

router = APIRouter()


def get_card_service() -> CardService:
    settings = get_settings()
    client = TrelloClient(api_key=settings.API_KEY, api_token=settings.API_TOKEN)
    return CardService(trello_client=client)


@router.post(
    "/sync",
    summary="Sync cards from Trello",
    description=(
        "Fetches all open cards from the configured Trello board "
        "and upserts them into the local MySQL database."
    ),
)
async def sync_cards(
    db: AsyncSession = Depends(get_db),
    service: CardService = Depends(get_card_service),
) -> dict:
    settings = get_settings()
    synced = await service.sync_board_cards(db, board_id=settings.BOARD_ID)
    return {"synced": synced, "board_id": settings.BOARD_ID}
