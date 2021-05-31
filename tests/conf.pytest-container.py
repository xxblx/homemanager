
import multiprocessing
import nacl.utils

DB_SETTINGS = {
    'database': 'testdb',
    'user': 'hmuser',
    'host': '/var/run/postgresql'
}

DEBUG = True
HOST = 'localhost'
PORT = 8888
WORKERS = multiprocessing.cpu_count()
MAC_KEY = nacl.utils.random(size=64)
COOKIE_SECRET = nacl.utils.random(size=64)
TOKEN_EXPIRES_TIME = 7200

LOCATION = {
    'name': 'London',
    'region': 'England',
    'timezone': 'Europe/London',
    'latitude': 51.473333333333336,
    'longitude': -0.0008333333333333334
}

NOTIFICATIONS_SETTINGS = {
    'telegram': False,
    'date_format': '%d.%m.%Y %H:%M:%S'
}

TELEGRAM_SETTINGS = {
    'bot_id': '0',
    'chat_id': 0,
    'proxy': {}
}
