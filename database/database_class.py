import asyncio
import asyncpg

from config.config import POSTGRES_CONFIG


class DatabaseAPI(object):
    """
    Класс для работы с базой данных Postgres
    """

    @classmethod
    async def connect_to_database(cls):
        """
        Создаём подключение к базе данных
        """
        self = DatabaseAPI()
        self.pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
        return self

    def connect(func):
        """
        Декоратор для осуществления запросов к базе данных
        """
        async def decorator(self, *args, **kwargs):
            async with self.pool.acquire() as connect:
                async with connect.transaction():
                    return await func(self, connect=connect, *args, **kwargs)
        return decorator


    @connect
    async def get_user_by_user_id(self, connect, user_id: int):
        """
        Получить пользователя по его Telegram-id
        """
        return await connect.fetchval('''SELECT * FROM users WHERE user_id = $1''', user_id)


    @connect
    async def add_new_user_to_database(self, connect, user_id: int, username: str):
        """
        Добавить нового пользователя в базу данных, внося его Telegram-id и username
        """
        return await connect.execute('''INSERT INTO users (user_id, username) VALUES ($1, $2)''', user_id, username)


    @connect
    async def get_phone_number(self, connect, phone: str):
        """
        Делает запрос в базу данных по введённому номеру телефона
        """
        return await connect.fetchval('''SELECT phone_number FROM phone_numbers WHERE phone_number = $1''', phone)


    @connect
    async def add_new_phone_number_to_database(self, connect, phone: str, added_by: str):
        """
        Добавить новый номер в базу данных
        """
        return await connect.execute('''INSERT INTO phone_numbers (phone_number, added_by) VALUES ($1, $2)''', phone,
                                     added_by)


    @connect
    async def get_message_by_id(self, connect, message_id: int):
        """
        Получить сообщение по его ID в базе данных
        """
        return await connect.fetchval('''SELECT message FROM messages WHERE id = $1''', message_id)

    @connect
    async def fully_clear_database(self, connect):
        """
        Полное очищение базы данных, за исключением таблицы messages
        """
        await connect.execute('''DELETE FROM phone_numbers''')
        await connect.execute('''DELETE FROM users''')

    @connect
    async def get_all_messages_with_id(self, connect):
        """
        Получить все сообщения с их id
        """
        return await connect.fetch('SELECT * FROM messages')

    @connect
    async def set_new_message(self, connect, id: int, message: str):
        """
        Изменить сообщение в базе данных
        """
        return await connect.execute('UPDATE messages SET message = $1 WHERE id = $2', message, id)

    @connect
    async def add_user_to_the_ban_list(self, connect, id: int):
        """
        Забанить пользователя
        """
        return await connect.execute('UPDATE users SET is_banned = true WHERE user_id = $1', id)

    @connect
    async def remove_user_from_the_ban_list(self, connect, id: int):
        """
        Разбанить пользователя
        """
        return await connect.execute('UPDATE users SET is_banned = false WHERE user_id = $1', id)

    @connect
    async def check_user_id_in_the_ban_list(self, connect, id: int):
        """
        Проверить забанен ли пользователь
        """
        return await connect.fetchval('''SELECT (is_banned) FROM users WHERE user_id = $1''', id)

    @connect
    async def get_all_user_ids(self, connect):
        """
        Получить Telegram-ID всех пользователей для рассылки
        """
        return await connect.fetch('''SELECT (user_id) FROM users WHERE is_banned = false''')


loop = asyncio.get_event_loop()
db = loop.run_until_complete(DatabaseAPI.connect_to_database())