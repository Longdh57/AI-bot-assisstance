from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.external.trello.client import TrelloClient
from app.models.trello_list import TrelloList


def _to_orm_dict(raw: dict) -> dict:
    """Map a raw Trello list response (camelCase) to ORM column names (snake_case)."""
    return {
        "id": raw.get("id"),
        "id_board": raw.get("idBoard"),
        "name": raw.get("name", ""),
        "closed": raw.get("closed", False),
        "subscribed": raw.get("subscribed", False),
        "pos": raw.get("pos", 0.0),
        "soft_limit": str(raw["softLimit"]) if raw.get("softLimit") is not None else None,
        "limits": raw.get("limits") or {},
    }


class ListService:
    """Business logic for syncing Trello lists into local MySQL."""

    def __init__(self, trello_client: TrelloClient) -> None:
        self._trello = trello_client

    async def fetch_board_lists(self, board_id: str) -> list[dict]:
        """Fetch raw list data from Trello (HTTP only, no DB)."""
        return await self._trello.get_board_lists(board_id)

    async def upsert_lists(self, db: AsyncSession, raw_lists: list[dict]) -> int:
        """Upsert a pre-fetched list of raw Trello lists into local DB.

        Returns the number of lists upserted.
        """
        if not raw_lists:
            return 0

        rows = [_to_orm_dict(l) for l in raw_lists]

        stmt = insert(TrelloList).values(rows)
        update_cols = {col: stmt.inserted[col] for col in rows[0] if col != "id"}
        stmt = stmt.on_duplicate_key_update(**update_cols)

        await db.execute(stmt)
        await db.commit()

        return len(rows)

    async def sync_board_lists(self, db: AsyncSession, board_id: str) -> int:
        """Fetch and upsert all lists for a board (convenience method)."""
        raw_lists = await self.fetch_board_lists(board_id)
        return await self.upsert_lists(db, raw_lists)
