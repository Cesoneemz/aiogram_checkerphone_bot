from aiogram import types
from aiogram.dispatcher import FSMContext

from load import dp
from database.database_class import db
from states.states import WaitPhoneNumber

from config.config import ADMIN_ID
from utils.validators import validation_is_banned


@dp.message_handler(commands=['start', 'help'])
@validation_is_banned
async def send_welcome(message: types.Message):
    if await db.get_user_by_user_id(user_id=message.from_user.id) is None:
        await db.add_new_user_to_database(user_id=message.from_user.id, username=message.from_user.username)
    await message.answer(await db.get_message_by_id(message_id=1), parse_mode='HTML')


@dp.message_handler(lambda message: message.text == 'Проверить номер')
@validation_is_banned
async def get_or_add_phone_number_part1(message: types.Message):
    await message.answer(await db.get_message_by_id(message_id=2), parse_mode='HTML')

    await WaitPhoneNumber.wait_for_phone_number.set()


@dp.message_handler(state=WaitPhoneNumber.wait_for_phone_number)
@validation_is_banned
async def get_or_add_phone_number_part2(message: types.Message, state: FSMContext):
    from utils.validators import validation_phone_number

    if validation_phone_number(phone=message.text) and await db.get_phone_number(phone=message.text) is None:

        added_by = "Номер добавлен администратором" if str(message.from_user.id) in ADMIN_ID \
            else f"Номер добавлен пользователем {message.from_user.username}, его ID: {message.from_user.id}"

        await db.add_new_phone_number_to_database(phone=message.text, added_by=added_by)

        await message.answer(await db.get_message_by_id(message_id=3), parse_mode='HTML')

    elif not validation_phone_number(phone=message.text):

        await message.answer(await db.get_message_by_id(message_id=4), parse_mode='HTML')

    elif not await db.get_phone_number(phone=message.text) is None:

        await message.answer(await db.get_message_by_id(message_id=5), parse_mode='HTML')

    await state.finish()
