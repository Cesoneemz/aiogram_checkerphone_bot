import asyncio

from aiogram import executor

from config.config import ADMIN_ID
from load import bot


async def on_startup(dp):
    """
    При старте бота рассылает всем админам из списка фразу Bot has been started
    """
    for id in ADMIN_ID:
        await bot.send_message(id, 'Bot has been started')


async def on_shutdown(dp):
    await bot.close()


if __name__ == '__main__':
    from handlers.handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
