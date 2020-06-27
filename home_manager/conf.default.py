DSN = 'dbname=testdb user=testuser password=testpassword host=127.0.0.1'
DEBUG = True
HOST = '127.0.0.1'
PORT = 8888

# Location is used with `Location` from `astral` module
# https://astral.readthedocs.io/en/stable/index.html#locations
LOCATION = (
    'London',  # city
    'England',  # region
    0,  # latitude
    0,  # longitude
    'Europe/London',  # time zone
    0  # elevation
)

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
