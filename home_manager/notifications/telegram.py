# -*- coding: utf-8 -*-

import requests

from .base import BaseBackend
from ..conf import TELEGRAM_SETTINGS


class TelegramBackend(BaseBackend):
    base_url = 'https://api.telegram.org/bot%s'
    photo_url = base_url + '/sendPhoto'
    message_url = base_url + '/sendMessage'

    def __init__(self, loop):
        self.loop = loop
        self.bot_id = TELEGRAM_SETTINGS['bot_id']
        self.chat_id = TELEGRAM_SETTINGS['chat_id']
        self.photo_url = self.photo_url % self.bot_id
        self.message_url = self.message_url % self.bot_id

    @BaseBackend.run_in_loop_executor
    def send_notification(self, date_str, identity, photo):
        requests.post(
            url=self.photo_url,
            files={'photo': photo},
            data={
                'chat_id': self.chat_id,
                'caption': '{} - {} #motion'.format(date_str, identity)
            },
            proxies=TELEGRAM_SETTINGS['proxy']
        )

    @BaseBackend.run_in_loop_executor
    def send_log(self, date_str, identity, status='on'):
        text = '{} - {} - motion detection: {} #log'.format(
            date_str,
            identity,
            status
        )
        requests.post(
            url=self.message_url,
            data={
                'chat_id': self.chat_id,
                'text': text
            },
            proxies=TELEGRAM_SETTINGS['proxy']
        )
