from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card
from app.models.current_list import CurrentList
from app.models.trello_list import TrelloList
from app.schemas.current_list import CardInCurrentList, CurrentListWithCards


class CurrentListService:
    """Business logic for managing current lists and retrieving their cards."""

    async def get_all(self, db: AsyncSession) -> list[CurrentList]:
        result = await db.execute(select(CurrentList))
        return list(result.scalars().all())

    async def add(self, db: AsyncSession, list_id: str) -> CurrentList:
        existing = await db.execute(
            select(CurrentList).where(CurrentList.list_id == list_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"List '{list_id}' is already marked as current.")

        entry = CurrentList(list_id=list_id)
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    async def remove(self, db: AsyncSession, list_id: str) -> None:
        result = await db.execute(
            select(CurrentList).where(CurrentList.list_id == list_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            raise HTTPException(status_code=404, detail=f"List '{list_id}' is not marked as current.")

        await db.delete(entry)
        await db.commit()

    async def get_current_cards(self, db: AsyncSession) -> list[CurrentListWithCards]:
        """Return cards grouped by their current list, with list name resolved."""

        # 1. Load all current list IDs
        result = await db.execute(select(CurrentList))
        current_list_ids = [row.list_id for row in result.scalars().all()]

        if not current_list_ids:
            return []

        # 2. Resolve list names from trello_lists
        result = await db.execute(
            select(TrelloList).where(TrelloList.id.in_(current_list_ids))
        )
        lists_by_id: dict[str, TrelloList] = {lst.id: lst for lst in result.scalars().all()}

        # 3. Fetch cards that belong to any current list
        result = await db.execute(
            select(Card).where(Card.id_list.in_(current_list_ids))
        )
        cards = result.scalars().all()

        # 4. Group cards by list, preserving current_list_ids order
        grouped: dict[str, CurrentListWithCards] = {}
        for list_id in current_list_ids:
            trello_list = lists_by_id.get(list_id)
            grouped[list_id] = CurrentListWithCards(
                list_id=list_id,
                list_name=trello_list.name if trello_list else "Unknown",
                cards=[],
            )

        for card in cards:
            if card.id_list in grouped:
                grouped[card.id_list].cards.append(CardInCurrentList.model_validate(card))

        return list(grouped.values())


current_list_service = CurrentListService()
