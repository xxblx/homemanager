from .telegram import TelegramBackend
from ..conf import NOTIFICATIONS_SETTINGS


class NotificationManager:
    def __init__(self, loop):
        self.loop = loop
        self.backends = set()

        if NOTIFICATIONS_SETTINGS['telegram']:
            tg = TelegramBackend(self.loop)
            self.backends.add(tg)

    async def send_notification(self, _datetime, identity, photo):
        date_str = _datetime.strftime(NOTIFICATIONS_SETTINGS['date_format'])
        for backend in self.backends:
            await backend.send_notification(date_str, identity, photo)

    async def send_log(self, _datetime, identity, status):
        date_str = _datetime.strftime(NOTIFICATIONS_SETTINGS['date_format'])
        for backend in self.backends:
            await backend.send_log(date_str, identity, status)
