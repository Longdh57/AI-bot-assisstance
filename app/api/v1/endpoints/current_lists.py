from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.external.discord.client import DiscordClient
from app.schemas.current_list import (
    AddCurrentListRequest,
    CurrentListResponse,
    CurrentListWithCards,
)
from app.services.current_list_service import current_list_service

router = APIRouter()


def get_discord_client() -> DiscordClient:
    settings = get_settings()
    if not settings.DISCORD_WEBHOOK:
        raise HTTPException(status_code=503, detail="DISCORD_WEBHOOK is not configured in .env")
    return DiscordClient(webhook_url=settings.DISCORD_WEBHOOK)


def _format_current_cards_message(groups: list[CurrentListWithCards]) -> str:
    """Build a Discord message from current list groups.

    Format:
        📋 Today's Tasks

        **List Name**
        • Card name (Due: YYYY-MM-DD)
        • Card name
    """
    today = datetime.now().strftime("%d-%m-%Y")
    lines = [f"📋 **Today's Tasks** - {today}"]

    for group in groups:
        lines.append(f"\n**{group.list_name}**")
        if not group.cards:
            lines.append("_No cards_")
        else:
            for card in group.cards:
                due = f" (Due: {card.due})" if card.due else ""
                lines.append(f"• {card.name}{due}")

    return "\n".join(lines)


@router.get(
    "",
    response_model=list[CurrentListResponse],
    summary="Get all current lists",
    description="Returns all Trello list IDs that are marked as current (today's task lists).",
)
async def get_current_lists(db: AsyncSession = Depends(get_db)) -> list[CurrentListResponse]:
    entries = await current_list_service.get_all(db)
    return [CurrentListResponse.model_validate(e) for e in entries]


@router.post(
    "",
    response_model=CurrentListResponse,
    status_code=201,
    summary="Add a current list",
    description="Mark a Trello list ID as current. Cards in this list are treated as today's tasks.",
)
async def add_current_list(
    body: AddCurrentListRequest,
    db: AsyncSession = Depends(get_db),
) -> CurrentListResponse:
    entry = await current_list_service.add(db, list_id=body.list_id)
    return CurrentListResponse.model_validate(entry)


@router.delete(
    "/{list_id}",
    status_code=204,
    summary="Remove a current list",
    description="Unmark a Trello list ID as current.",
)
async def remove_current_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    await current_list_service.remove(db, list_id=list_id)


@router.get(
    "/cards",
    response_model=list[CurrentListWithCards],
    summary="Get cards from current lists",
    description=(
        "Returns all cards that belong to current lists, "
        "grouped by list with list_id and list_name included."
    ),
)
async def get_current_cards(
    db: AsyncSession = Depends(get_db),
) -> list[CurrentListWithCards]:
    return await current_list_service.get_current_cards(db)


@router.post(
    "/notify-discord",
    summary="Send current cards to Discord",
    description=(
        "Sends current cards grouped by list to the Discord webhook. "
        "Each list shows card name and due date (if set)."
    ),
)
async def notify_discord(
    db: AsyncSession = Depends(get_db),
    discord_client: DiscordClient = Depends(get_discord_client),
) -> dict:
    groups = await current_list_service.get_current_cards(db)

    message = _format_current_cards_message(groups)
    await discord_client.send_message(message)

    total_cards = sum(len(g.cards) for g in groups)
    return {
        "lists": len(groups),
        "cards": total_cards,
        "message": "Notification sent to Discord.",
    }
