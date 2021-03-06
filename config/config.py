import os

API_TOKEN = os.getenv('API_TOKEN_THREE')

ADMIN_ID = os.getenv('ADMIN_IDS').split(' ')

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'port': os.getenv('POSTGRES_PORT'),
    'database': os.getenv('POSTGRES_DATABASE_THREE')
}