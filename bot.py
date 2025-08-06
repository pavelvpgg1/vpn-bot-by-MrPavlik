import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers.user import router as user_router
from utils.logger import setup_logger


async def main():
    """Главная функция создания бота"""
    setup_logger()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(user_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
