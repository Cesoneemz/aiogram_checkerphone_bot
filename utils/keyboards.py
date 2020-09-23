from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
load_phone_numbers_in_database = KeyboardButton(text="Загрузить номера телефонов")
unload_phone_numbers_in_database = KeyboardButton(text="Выгрузить номера телефонов")
fully_clear_database = KeyboardButton(text="Очистить базу данных")
add_new_admin = KeyboardButton(text="Добавить нового админа")
delete_admin = KeyboardButton(text="Удалить админа")
edit_bots_messages = KeyboardButton(text="Изменить сообщения бота")
add_user_to_ban_list = KeyboardButton(text="Забанить пользователя")
delete_user_from_ban_list = KeyboardButton(text="Разбанить пользователя")
send_mailing = KeyboardButton(text="Рассылка")
get_csv_file_with_users = KeyboardButton(text="Получить csv-файл с пользователями")
admin_keyboard.add(load_phone_numbers_in_database, unload_phone_numbers_in_database, fully_clear_database, add_new_admin, delete_admin, edit_bots_messages, add_user_to_ban_list, delete_user_from_ban_list, send_mailing, get_csv_file_with_users)



