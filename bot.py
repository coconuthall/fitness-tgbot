import logging
import asyncio
from aiogram import Bot, Dispatcher, executor
from aiogram.types.bot_command import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from database.db import db_init, get_all_users
from config import load_config
from handlers import registration, common, statistics

from handlers.scheduled import schedule_all




async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/help", description="Информация о боте"),
        BotCommand(command="/begin", description="Начать отслеживать вес"),
        BotCommand(command="/cancel", description="Отменить текущее действие"),
        BotCommand(command="/quit", description="Прекратить отслеживать вес"),
        BotCommand(command="/statistics", description="Отследить прогресс"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(_):
    await set_commands(bot)
    registration.register_handlers(dp)
    statistics.register_handlers(dp)
    common.register_handlers(dp)
    await db_init()
    await schedule_all(bot)
    

    
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = load_config("botconfig.ini")

    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
