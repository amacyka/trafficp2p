from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import desc, select

from app.config import settings
from app.database.db import SessionLocal
from app.database.models import MarketSnapshot, Trade
from app.bot.keyboards import main_keyboard

router = Router()


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "📊 Crypto Liquidity Monitor\n\n"
        "Read-only MVP for market analytics.\n"
        f"Pair: {settings.symbol}",
        reply_markup=main_keyboard(),
    )


@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer(
        "/start — menu\n"
        "/market — latest market snapshot\n"
        "/orderbook — order-book placeholder\n"
        "/trades — recent trades placeholder"
    )


async def latest_snapshot() -> MarketSnapshot | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(MarketSnapshot)
            .where(MarketSnapshot.symbol == settings.symbol)
            .order_by(desc(MarketSnapshot.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()


async def market_text() -> str:
    row = await latest_snapshot()
    if not row:
        return "Нет данных. Collector ещё не получил первый snapshot."

    def f(value):
        return "—" if value is None else f"{value:,.6f}"

    return (
        f"📈 {row.exchange.upper()} — {row.symbol}\n\n"
        f"Bid: {f(row.bid)}\n"
        f"Ask: {f(row.ask)}\n"
        f"Last: {f(row.last_price)}\n"
        f"Spread: {f(row.spread_pct)}%\n"
        f"24h volume: {f(row.volume_24h)}\n\n"
        f"Updated: {row.timestamp} UTC"
    )


@router.message(Command("market"))
async def market(message: Message) -> None:
    await message.answer(await market_text(), reply_markup=main_keyboard())


@router.callback_query(lambda c: c.data == "market")
async def market_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        await market_text(), reply_markup=main_keyboard()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "/start — menu\n"
        "/market — current snapshot\n"
        "/orderbook — order book\n"
        "/trades — recent trades",
        reply_markup=main_keyboard(),
    )
    await callback.answer()


@router.message(Command("orderbook"))
async def orderbook(message: Message) -> None:
    await message.answer(
        "💧 Order book collector is the next adapter step.\n"
        "The xRocket provider-specific response parser belongs in "
        "app/exchanges/xrocket.py."
    )


@router.callback_query(lambda c: c.data == "orderbook")
async def orderbook_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "💧 Order book collector is the next adapter step.\n"
        "Keep provider-specific parsing in app/exchanges/xrocket.py."
    )
    await callback.answer()


@router.message(Command("trades"))
async def trades(message: Message) -> None:
    await message.answer(
        "📊 Trade-history collector is the next adapter step.\n"
        "The database already contains a trades table for this extension."
    )


@router.callback_query(lambda c: c.data == "trades")
async def trades_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "📊 Trade-history collector is the next adapter step."
    )
    await callback.answer()
