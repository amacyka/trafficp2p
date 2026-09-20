from __future__ import annotations

from typing import Any

import aiohttp


class XRocketClient:
    """Small read-only REST adapter.

    xRocket API paths can change. Keep all provider-specific paths here so the
    rest of the application remains provider-agnostic.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def ticker(self, symbol: str) -> Any:
        # Verify current path/parameter names in official xRocket docs.
        return await self._get("/v1/ticker", {"symbol": symbol})

    async def orderbook(self, symbol: str) -> Any:
        return await self._get("/v1/orderbook", {"symbol": symbol})

    async def trades(self, symbol: str, limit: int = 50) -> Any:
        return await self._get("/v1/trades", {"symbol": symbol, "limit": limit})
