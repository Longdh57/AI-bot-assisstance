import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.external.trello.client import TrelloClient
from app.services.card_service import CardService
from app.services.list_service import ListService

router = APIRouter()


def get_trello_client() -> TrelloClient:
    settings = get_settings()
    return TrelloClient(api_key=settings.API_KEY, api_token=settings.API_TOKEN)


def get_card_service(client: TrelloClient = Depends(get_trello_client)) -> CardService:
    return CardService(trello_client=client)


def get_list_service(client: TrelloClient = Depends(get_trello_client)) -> ListService:
    return ListService(trello_client=client)


@router.post(
    "/sync",
    summary="Sync cards and lists from Trello",
    description=(
        "Fetches all lists and open cards from the configured Trello board "
        "and upserts them into the local MySQL database."
    ),
)
async def sync_cards(
    db: AsyncSession = Depends(get_db),
    card_service: CardService = Depends(get_card_service),
    list_service: ListService = Depends(get_list_service),
) -> dict:
    settings = get_settings()
    board_id = settings.BOARD_ID

    # Step 1: fetch from Trello in parallel (independent HTTP calls, no shared state)
    raw_lists, raw_cards = await asyncio.gather(
        list_service.fetch_board_lists(board_id),
        card_service.fetch_board_cards(board_id),
    )

    # Step 2: write to DB sequentially (single session cannot handle concurrent commits)
    lists_synced = await list_service.upsert_lists(db, raw_lists)
    cards_synced = await card_service.upsert_cards(db, raw_cards)

    return {
        "board_id": board_id,
        "lists_synced": lists_synced,
        "cards_synced": cards_synced,
    }
