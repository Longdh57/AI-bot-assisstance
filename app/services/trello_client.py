import httpx
from fastapi import HTTPException


class TrelloClient:
    """Async HTTP client for the Trello REST API v1."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self, api_key: str, api_token: str) -> None:
        self._auth = {"key": api_key, "token": api_token}

    async def get_board_cards(self, board_id: str) -> list[dict]:
        """Fetch all open cards from a Trello board.

        GET /boards/{id}/cards
        """
        url = f"{self.BASE_URL}/boards/{board_id}/cards"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=self._auth)
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
