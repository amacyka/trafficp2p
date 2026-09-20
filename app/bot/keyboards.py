from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📈 Market", callback_data="market"),
                InlineKeyboardButton(text="💧 Order Book", callback_data="orderbook"),
            ],
            [
                InlineKeyboardButton(text="📊 Trades", callback_data="trades"),
                InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
            ],
        ]
    )
