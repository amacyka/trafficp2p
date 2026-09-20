from __future__ import annotations

from typing import Any

import aiohttp


class XRocketClient:
    """Read-only REST adapter for the real xRocket Exchange API.

    Verified against https://docs.pp.xrocket.exchange/api/exchange/reference
    on 2026-09-20. Symbols use a hyphen, e.g. "TON-USDT", "BTC-USDT".
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

    async def ticker_24h(self, symbol: str) -> dict[str, Any] | None:
        """GET /api/v1/ticker/24h?symbols=SYMBOL

        Returns the single ticker dict for `symbol`, or None if not found.
        Fields: symbol, open, close, high, low, changeRate, changePrice,
        baseVolume, quoteVolume, last (all strings).
        """
        data = await self._get("/api/v1/ticker/24h", {"symbols": symbol})
        tickers = data.get("tickers", [])
        for t in tickers:
            if t.get("symbol") == symbol:
                return t
        return tickers[0] if tickers else None

    async def orderbook(self, symbol: str, depth: int = 5) -> dict[str, Any]:
        """GET /api/v1/orderbook?symbol=SYMBOL&depth=5

        Returns {"sequence", "bids": [[price, size], ...], "asks": [...],
        "askTotalAmount", "bidTotalAmount"}. Prices/sizes are strings.
        """
        return await self._get(
            "/api/v1/orderbook", {"symbol": symbol, "depth": depth}
        )

    async def trades(self, symbol: str, limit: int = 50) -> Any:
        return await self._get(
            "/api/v1/trades", {"symbol": symbol, "limit": limit}
        )
