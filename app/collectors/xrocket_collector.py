from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.analytics.market import spread_pct
from app.config import settings
from app.database.db import SessionLocal
from app.database.models import MarketSnapshot
from app.exchanges.xrocket import XRocketClient


def _to_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


async def collect_once(client: XRocketClient) -> None:
    symbol = settings.symbol

    ticker = await client.ticker_24h(symbol)
    book = await client.orderbook(symbol, depth=5)

    last_price = _to_float(ticker.get("last")) if ticker else None
    volume_24h = _to_float(ticker.get("baseVolume")) if ticker else None

    bids = book.get("bids") or []
    asks = book.get("asks") or []
    bid = _to_float(bids[0][0]) if bids else None
    ask = _to_float(asks[0][0]) if asks else None

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    async with SessionLocal() as session:
        session.add(
            MarketSnapshot(
                timestamp=now,
                exchange="xrocket",
                symbol=symbol,
                bid=bid,
                ask=ask,
                last_price=last_price,
                spread_pct=spread_pct(bid, ask),
                volume_24h=volume_24h,
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
