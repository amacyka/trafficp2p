from __future__ import annotations

import asyncio
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
    await init_db()

    # Free hosting plans (e.g. Render's free tier) only offer a web service,
    # not a separate always-on worker. So the collector and the Telegram bot
    # run as background tasks inside this same web process.
    from app.collectors.xrocket_collector import run_collector

    app.state.collector_task = asyncio.create_task(run_collector())

    if settings.telegram_bot_token:
        from aiogram import Bot, Dispatcher

        from app.bot.handlers import router

        bot = Bot(settings.telegram_bot_token)
        dp = Dispatcher()
        dp.include_router(router)

        app.state.bot = bot
        app.state.bot_task = asyncio.create_task(dp.start_polling(bot))
        print("[web] Telegram bot polling started alongside the dashboard.")
    else:
        print(
            "[web] TELEGRAM_BOT_TOKEN not set — running the dashboard and "
            "collector only, no Telegram bot."
        )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    for attr in ("collector_task", "bot_task"):
        task = getattr(app.state, attr, None)
        if task is not None:
            task.cancel()

    bot = getattr(app.state, "bot", None)
    if bot is not None:
        await bot.session.close()


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
