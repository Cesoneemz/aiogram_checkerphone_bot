import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.validators import validation_is_admin, validation_phone_number

from load import dp, bot
from database.database_class import db
from utils.keyboards import admin_keyboard as ak
from states.states import WaitForCsvWithPhoneNumbers, ClearDatabase, AddAdmin, DeleteAdmin, EditSystemMessages, BanUser, \
    UnBanUser, Mailing
from config.config import POSTGRES_CONFIG, ADMIN_ID


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), commands=['admin'])
async def send_admin_keyboard(message: types.Message):
    await message.answer(await db.get_message_by_id(message_id=6), parse_mode='HTML', reply_markup=ak)


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id) and message.text == 'Загрузить номера '
                                                                                                  'телефонов')
async def load_phone_numbers_to_database_part1(message: types.Message):
    await message.answer(await db.get_message_by_id(message_id=9))

    await WaitForCsvWithPhoneNumbers.wait_for_csv_file.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), content_types=types.ContentType.DOCUMENT,
                    state=WaitForCsvWithPhoneNumbers.wait_for_csv_file)
async def load_phone_numbers_to_database_part2(message: types.Message, state: FSMContext):
    import os, csv, psycopg2

    file_id = message.document.file_id
    filename = message.document.file_name
    file = await bot.get_file(file_id=file_id)
    file_path = file.file_path

    destination = os.path.join(os.getcwd(), 'csv', filename)

    await bot.download_file(file_path=file_path, destination=destination)

    await message.answer(await db.get_message_by_id(message_id=10))

    connect = psycopg2.connect(**POSTGRES_CONFIG)
    connect.autocommit = True
    cursor = connect.cursor()

    error_numbers = {}

    with open(destination, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 1:
                split_row = row[0].split(';')
            else:
                split_row = row
            if await db.get_phone_number(phone=split_row[0]) is None and validation_phone_number(phone=split_row[0]):
                await db.add_new_phone_number_to_database(phone=split_row[0], added_by='Номер добавлен администратором')
            elif not validation_phone_number(phone=split_row[0]):
                error_numbers[str(split_row[0])] = await db.get_message_by_id(message_id=4)
            elif not await db.get_phone_number(phone=split_row[0]) is None:
                error_numbers[str(split_row[0])] = await db.get_message_by_id(message_id=5)

    connect.commit()

    os.remove(destination)

    await state.finish()

    send_message = "Номера были успешно загружены."

    if error_numbers:
        send_message += " Некоторые номера были загружены с ошибками.\n\n"
        for number, error in error_numbers.items():
            send_message += f"Номер: {number}, ошибка: {error}\n"

    await message.answer(send_message, parse_mode='HTML')


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id) and message.text == 'Выгрузить номера '
                                                                                                  'телефонов')
async def unload_csv_with_phone_numbers(message: types.Message):
    import os
    import psycopg2

    filename = 'phone_numbers.csv'
    path = os.path.join(os.getcwd(), 'csv', filename)
    connect = psycopg2.connect(**POSTGRES_CONFIG)
    connect.autocommit = True
    cursor = connect.cursor()

    with open(path, 'w') as f:
        sqlstr = "COPY public.phone_numbers TO STDOUT DELIMITER ',' CSV ENCODING 'UTF-8'"
        cursor.copy_expert(sql=sqlstr, file=f)
    with open(path, 'rb') as f:
        await bot.send_document(chat_id=message.from_user.id, document=f)

    os.remove(path)


@dp.message_handler(
    lambda message: validation_is_admin(message.from_user.id) and message.text == "Очистить базу данных")
async def clear_info_database_yesno(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Да", callback_data="yes")],
            [InlineKeyboardButton(text="Нет", callback_data="no")],
        ]
    )
    await message.answer("Вы точно хотите очистить базу с информацией?", reply_markup=markup)

    await ClearDatabase.yesno_prompt.set()


@dp.callback_query_handler(lambda call: validation_is_admin(call.from_user.id), state=ClearDatabase.yesno_prompt)
async def clear_info_database(call: types.CallbackQuery, state: FSMContext):
    if call.data == "no":
        await state.finish()

        await bot.send_message(chat_id=call.from_user.id, text="Отменено.")

    else:

        await db.fully_clear_database()
        await bot.send_message(chat_id=call.from_user.id, text="База данных была полностью очищена.")

        await state.finish()


@dp.message_handler(
    lambda message: validation_is_admin(message.from_user.id) and message.text == 'Добавить нового админа')
async def add_admin_part_1(message: types.Message):
    await message.answer("Пожалуйста, введите ID нового админа")

    await AddAdmin.wait_for_admin_id.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), state=AddAdmin.wait_for_admin_id)
async def add_admin_part2(message: types.Message, state: FSMContext):
    if message.text not in ADMIN_ID:
        ADMIN_ID.append(message.text)
    await message.answer(f"ID {message.text} был добавлен к списку админов")

    await state.finish()


@dp.message_handler(
    lambda message: validation_is_admin(message.from_user.id) and message.text == 'Удалить')
async def add_admin_part_1(message: types.Message):
    await message.answer("Пожалуйста, введите ID админа, которого нужно удалить")

    await DeleteAdmin.wait_for_admin_id_delete.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id),
                    state=DeleteAdmin.wait_for_admin_id_delete)
async def add_admin_part2(message: types.Message, state: FSMContext):
    if message.text in ADMIN_ID:
        ADMIN_ID.remove(message.text)
        await message.answer(f"Админ с ID {message.text} был удалён")
    else:
        await message.answer('Такого админа нет')

    await state.finish()


@dp.message_handler(
    lambda message: validation_is_admin(message.from_user.id) and message.text == 'Изменить сообщения бота')
async def edit_system_messages_id(message: types.Message):
    messages = await db.get_all_messages_with_id()
    msg = ''
    for i in messages:
        msg += f'ID: {i[0]}   Сообщение: {i[1]}\n\n'
    await message.answer(msg)
    await message.answer(await db.get_message_by_id(message_id=11))
    await EditSystemMessages.wait_for_id.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), state=EditSystemMessages.wait_for_id)
async def edit_system_message(message: types.Message, state: FSMContext):
    await state.update_data(id=int(message.text))
    await message.answer(await db.get_message_by_id(message_id=12))

    await EditSystemMessages.wait_for_new_message.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id),
                    state=EditSystemMessages.wait_for_new_message)
async def set_new_system_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get('id')

    try:
        await db.set_new_message(id=id, message=message.text)

        await message.answer(await db.get_message_by_id(message_id=13))

        await state.finish()

    except Exception:

        await message.answer(await db.get_message_by_id(message_id=14))
        await state.finish()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id) and message.text == 'Забанить '
                                                                                                  'пользователя')
async def add_user_to_the_ban_list_part1(message: types.Message):
    await message.answer(await db.get_message_by_id(message_id=15))

    await BanUser.wait_for_id.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), state=BanUser.wait_for_id)
async def add_user_to_the_ban_list_part2(message: types.Message, state: FSMContext):
    try:

        await db.add_user_to_the_ban_list(id=int(message.text))
        await message.answer(await db.get_message_by_id(message_id=16))

        await state.finish()

    except Exception as e:
        await message.answer("Ошибка")
        print(e)

        await state.finish()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id) and message.text == 'Разбанить '
                                                                                                  'пользователя')
async def add_user_to_the_ban_list_part1(message: types.Message):
    await message.answer(await db.get_message_by_id(message_id=17))

    await UnBanUser.wait_for_id.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), state=UnBanUser.wait_for_id)
async def add_user_to_the_ban_list_part1(message: types.Message, state: FSMContext):
    try:

        await db.remove_user_from_the_ban_list(id=int(message.text))
        await message.answer(await db.get_message_by_id(message_id=18))

        await state.finish()

    except Exception as e:
        await message.answer("Ошибка")

        await state.finish()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id) and message.text == "Рассылка")
async def mailing(message: types.Message):
    await message.answer("Пришлите текст рассылки")

    await Mailing.wait_for_text.set()


@dp.message_handler(lambda message: validation_is_admin(message.from_user.id), state=Mailing.wait_for_text)
async def send_mailing(message: types.Message, state: FSMContext):
    users_ids = await db.get_all_user_ids()
    for id in users_ids:
        try:
            await bot.send_message(chat_id=id['user_id'], text=message.text)

            await asyncio.sleep(0.3)
        except Exception:
            pass

    await state.finish()


@dp.message_handler(
    lambda message: str(message.from_user.id) in ADMIN_ID and message.text == 'Получить csv-файл с пользователями')
async def send_csv_with_users(message: types.Message):
    import os
    import psycopg2

    filename = 'users.csv'
    path = os.path.join(os.getcwd(), 'csv', filename)
    connect = psycopg2.connect(**POSTGRES_CONFIG)
    connect.autocommit = True
    cursor = connect.cursor()

    with open(path, 'w') as f:
        sqlstr = "COPY public.users TO STDOUT DELIMITER ',' CSV ENCODING 'UTF-8'"
        cursor.copy_expert(sql=sqlstr, file=f)
    with open(path, 'rb') as f:
        await bot.send_document(chat_id=message.from_user.id, document=f)
