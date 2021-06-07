
import multiprocessing
import nacl.utils

DB_SETTINGS = {
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpassword',
    'host': '127.0.0.1'
}

DEBUG = True
HOST = '127.0.0.1'
PORT = 8888
WORKERS = multiprocessing.cpu_count()
MAC_KEY = nacl.utils.random(size=64)
COOKIE_SECRET = nacl.utils.random(size=64)
TOKEN_EXPIRES_TIME = 7200  # seconds

# LOCATION is required to construct `astral.LocationInfo`
# Define custom location
# https://astral.readthedocs.io/en/latest/#custom-location
# Search location details with `database` and `lookup` from `astral.geocoder`
# https://astral.readthedocs.io/en/latest/#geocoder
LOCATION = {
    'name': 'London',
    'region': 'England',
    'timezone': 'Europe/London',
    'latitude': 51.473333333333336,
    'longitude': -0.0008333333333333334
}

NOTIFICATIONS_SETTINGS = {
    'telegram': False,
    # 'email': False,
    'date_format': '%d.%m.%Y %H:%M:%S'
}

TELEGRAM_SETTINGS = {
    'bot_id': '0',
    'chat_id': 0,

    # It is possible to use proxies if telegram is blocked in your region
    # 'proxy': {
    #     'http': 'http://192.168.1.1:8080',
    #     'https': 'http://192.168.1.1:8080'
    # }
    'proxy': {}
}
