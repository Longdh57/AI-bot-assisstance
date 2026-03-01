import httpx
from fastapi import HTTPException


class DiscordClient:
    """Async HTTP client for sending messages via a Discord webhook."""

    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    async def _post(self, payload: dict) -> None:
        """Execute a POST request to the Discord webhook."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._webhook_url, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Discord API error: {exc.response.text}",
                ) from exc
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not reach Discord API: {exc}",
                ) from exc

    async def send_message(self, content: str) -> None:
        """Send a text message to the configured Discord webhook channel.

        POST {webhook_url}
        Body: {"content": "..."}
        Success: 204 No Content
        """
        await self._post({"content": content})
