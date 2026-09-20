from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.analytics.market import spread_pct
from app.config import settings
from app.database.db import SessionLocal
from app.database.models import MarketSnapshot, Trade
from app.exchanges.xrocket import XRocketClient


def _extract_ticker(data: dict) -> tuple[float | None, float | None, float | None, float | None]:
    # Defensive parser: adapt these keys if the current xRocket response differs.
    payload = data.get("data", data)
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    return (
        payload.get("bid") or payload.get("bestBid"),
        payload.get("ask") or payload.get("bestAsk"),
        payload.get("last") or payload.get("lastPrice") or payload.get("price"),
        payload.get("volume24h") or payload.get("volume_24h") or payload.get("volume24H"),
    )


async def collect_once(client: XRocketClient) -> None:
    ticker = await client.ticker(settings.symbol)
    bid, ask, last_price, volume_24h = _extract_ticker(ticker)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    async with SessionLocal() as session:
        session.add(
            MarketSnapshot(
                timestamp=now,
                exchange="xrocket",
                symbol=settings.symbol,
                bid=float(bid) if bid is not None else None,
                ask=float(ask) if ask is not None else None,
                last_price=float(last_price) if last_price is not None else None,
                spread_pct=spread_pct(
                    float(bid) if bid is not None else None,
                    float(ask) if ask is not None else None,
                ),
                volume_24h=float(volume_24h) if volume_24h is not None else None,
            )
        )
        await session.commit()


async def run_collector() -> None:
    client = XRocketClient(settings.xrocket_api_base_url)

    while True:
        try:
            await collect_once(client)
        except Exception as exc:
            print(f"[collector] {type(exc).__name__}: {exc}")
        await asyncio.sleep(settings.collect_interval_seconds)
