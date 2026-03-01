import httpx
from fastapi import HTTPException


class TrelloClient:
    """Async HTTP client for the Trello REST API v1."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self, api_key: str, api_token: str) -> None:
        self._auth = {"key": api_key, "token": api_token}

    async def _get(self, path: str, **extra_params) -> list[dict] | dict:
        """Execute an authenticated GET request and return parsed JSON."""
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params={**self._auth, **extra_params})
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Trello API error: {exc.response.text}",
                ) from exc
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not reach Trello API: {exc}",
                ) from exc
        return response.json()

    async def get_board_cards(self, board_id: str) -> list[dict]:
        """Fetch all open cards from a Trello board.

        GET /boards/{id}/cards
        """
        return await self._get(f"/boards/{board_id}/cards")

    async def get_board_lists(self, board_id: str) -> list[dict]:
        """Fetch all lists from a Trello board.

        GET /boards/{id}/lists
        """
        return await self._get(f"/boards/{board_id}/lists", filter="all")
