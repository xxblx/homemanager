# -*- coding: utf-8 -*-

import requests

from .base import BaseBackend
from ..conf import TELEGRAM_SETTINGS


class TelegramBackend(BaseBackend):
    base_url = 'https://api.telegram.org/bot%s/sendPhoto'

    def __init__(self, loop):
        self.loop = loop
        self.bot_id = TELEGRAM_SETTINGS['bot_id']
        self.chat_id = TELEGRAM_SETTINGS['chat_id']
        self.url = self.base_url % self.bot_id

    @BaseBackend.run_in_loop_executor
    def send_notification(self, date_str, identity, photo):
        requests.post(
            url=self.url,
            files={'photo': photo},
            data={
                'chat_id': self.chat_id,
                'caption': '%s - %s' % (date_str, identity)
            },
            proxies=TELEGRAM_SETTINGS['proxy']
        )
