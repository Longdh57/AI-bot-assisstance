from datetime import date, datetime

from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card
from app.services.trello_client import TrelloClient


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_date(value: str | None) -> date | None:
    dt = _parse_dt(value)
    return dt.date() if dt else None


def _to_orm_dict(raw: dict) -> dict:
    """Map a raw Trello card response (camelCase) to ORM column names (snake_case)."""
    return {
        "id": raw.get("id"),
        "id_short": raw.get("idShort"),
        "id_board": raw.get("idBoard"),
        "id_list": raw.get("idList"),
        "id_attachment_cover": raw.get("idAttachmentCover"),
        "mirror_source_id": raw.get("mirrorSourceId"),
        "name": raw.get("name", ""),
        "short_link": raw.get("shortLink", ""),
        "short_url": raw.get("shortUrl", ""),
        "url": raw.get("url", ""),
        "desc": raw.get("desc", ""),
        "desc_data": raw.get("descData") or {},
        "closed": raw.get("closed", False),
        "subscribed": raw.get("subscribed", False),
        "manual_cover_attachment": raw.get("manualCoverAttachment", False),
        "date_last_activity": _parse_dt(raw.get("dateLastActivity")),
        "due": _parse_date(raw.get("due")),
        "due_reminder": str(raw["dueReminder"]) if raw.get("dueReminder") is not None else None,
        "address": raw.get("address"),
        "location_name": raw.get("locationName"),
        "coordinates": raw.get("coordinates"),
        "pos": raw.get("pos", 0.0),
        "card_role": raw.get("cardRole"),
        "creation_method": raw.get("creationMethod"),
        "id_members": raw.get("idMembers") or [],
        "id_members_voted": raw.get("idMembersVoted") or [],
        "id_checklists": raw.get("idChecklists") or [],
        "id_labels": raw.get("idLabels") or [],
        "labels": raw.get("labels") or [],
        "check_item_states": raw.get("checkItemStates") or [],
        "badges": raw.get("badges") or {},
        "cover": raw.get("cover") or {},
        "limits": raw.get("limits") or {},
    }


class CardService:
    """Business logic for syncing Trello cards into local MySQL."""

    def __init__(self, trello_client: TrelloClient) -> None:
        self._trello = trello_client

    async def sync_board_cards(self, db: AsyncSession, board_id: str) -> int:
        """Fetch all cards from a Trello board and upsert them into local DB.

        Returns the number of cards synced.
        """
        raw_cards = await self._trello.get_board_cards(board_id)

        if not raw_cards:
            return 0

        rows = [_to_orm_dict(c) for c in raw_cards]

        # MySQL upsert: INSERT ... ON DUPLICATE KEY UPDATE
        stmt = insert(Card).values(rows)
        update_cols = {col: stmt.inserted[col] for col in rows[0] if col != "id"}
        stmt = stmt.on_duplicate_key_update(**update_cols)

        await db.execute(stmt)
        await db.commit()

        return len(rows)
