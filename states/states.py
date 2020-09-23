from aiogram.dispatcher.filters.state import State, StatesGroup


class WaitPhoneNumber(StatesGroup):
    wait_for_phone_number = State()


class WaitForCsvWithPhoneNumbers(StatesGroup):
    wait_for_csv_file = State()


class ClearDatabase(StatesGroup):
    yesno_prompt = State()


class AddAdmin(StatesGroup):
    wait_for_admin_id = State()


class DeleteAdmin(StatesGroup):
    wait_for_admin_id_delete = State()


class EditSystemMessages(StatesGroup):
    wait_for_id = State()
    wait_for_new_message = State()


class BanUser(StatesGroup):
    wait_for_id = State()


class UnBanUser(StatesGroup):
    wait_for_id = State()

class Mailing(StatesGroup):
    wait_for_text = State()
