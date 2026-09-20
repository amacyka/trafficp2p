import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.collectors.xrocket_collector import run_collector
from app.config import settings
from app.database.db import init_db


async def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. Get a token from @BotFather in "
            "Telegram and set it as an environment variable."
        )

    await init_db()

    bot = Bot(settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    collector_task = asyncio.create_task(run_collector())

    try:
        print("Starting Telegram bot...")
        await dp.start_polling(bot)
    finally:
        collector_task.cancel()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
