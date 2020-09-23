import asyncio

from aiogram.types import Message

from config.config import ADMIN_ID
from database.database_class import db


def validation_phone_number(phone: str):
    import re

    regex = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', re.I)
    match = regex.match(str(phone))

    return bool(match)


def validation_is_admin(user_id: int):
    return True if str(user_id) in ADMIN_ID else False


def validation_is_banned(func):
    async def decorator(message: Message):
        user = await db.check_user_id_in_the_ban_list(id=message.from_user.id)
        await func(message) if not user else await message.answer("Вы были забанены")
    return decorator


