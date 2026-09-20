from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, select

from app.config import settings
from app.database.db import SessionLocal, init_db
from app.database.models import MarketSnapshot

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Crypto Liquidity Monitor")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    # Idempotent: safe even if the bot service already created the tables.
    await init_db()


def _serialize(row: MarketSnapshot) -> dict:
    return {
        "timestamp": row.timestamp.isoformat() + "Z",
        "exchange": row.exchange,
        "symbol": row.symbol,
        "bid": row.bid,
        "ask": row.ask,
        "last_price": row.last_price,
        "spread_pct": row.spread_pct,
        "volume_24h": row.volume_24h,
    }


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/market")
async def market() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            select(MarketSnapshot)
            .where(MarketSnapshot.symbol == settings.symbol)
            .order_by(desc(MarketSnapshot.timestamp))
            .limit(1)
        )
        row = result.scalar_one_or_none()

    if row is None:
        return {"symbol": settings.symbol, "status": "no_data"}

    return {"status": "ok", **_serialize(row)}


@app.get("/api/history")
async def history(limit: int = 200) -> dict:
    limit = max(1, min(limit, 1000))

    async with SessionLocal() as session:
        result = await session.execute(
            select(MarketSnapshot)
            .where(MarketSnapshot.symbol == settings.symbol)
            .order_by(desc(MarketSnapshot.timestamp))
            .limit(limit)
        )
        rows = list(result.scalars())

    rows.reverse()
    return {"symbol": settings.symbol, "points": [_serialize(r) for r in rows]}
