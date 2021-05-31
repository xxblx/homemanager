from functools import partial
from uuid import uuid4
from urllib.parse import urlencode

from tornado.httpclient import AsyncHTTPClient

from ..conf import TELEGRAM_SETTINGS


class TelegramBackend:
    base_url = 'https://api.telegram.org/bot{}'
    photo_url = base_url + '/sendPhoto'
    message_url = base_url + '/sendMessage'

    def __init__(self, loop):
        self.loop = loop
        self.http_client = AsyncHTTPClient()
        self.bot_id = TELEGRAM_SETTINGS['bot_id']
        self.chat_id = TELEGRAM_SETTINGS['chat_id']
        self.photo_url = self.photo_url.format(self.bot_id)
        self.message_url = self.message_url.format(self.bot_id)

    @staticmethod
    async def multipart_producer(boundary, chat_id, caption, photo, write):
        boundary_bytes = boundary.encode()

        # data params
        for key, value in (('chat_id', str(chat_id)), ('caption', caption)):
            await write(
                (b'--%s\r\n' % boundary_bytes) +
                (b'Content-Disposition: form-data; name="%s"\r\n\r\n%s'
                    % (key.encode(), value.encode())
                )
                + b'\r\n'
            )

        # name=photo
        await write(
            (b'--%s\r\n' % boundary_bytes) +
            b'Content-Disposition: form-data; name="photo"; filename="pic"\r\n'
            + b'\r\n'
        )

        # photo
        await write(photo)
        await write(b'\r\n')
        await write(b'--%s--\r\n' % (boundary_bytes,))

    async def send_notification(self, date_str, identity, photo):
        """ Send a photo to a telegram chat when the motion has been detected

        :param date_str: date and time when the event happened
        :type date_str: str
        :param identity: which camera made a photo
        :type identity: str
        :param photo: a picture captured by a camera
        :type photo: bytes
        """
        caption = '{} - {} #motion'.format(date_str, identity)
        boundary = uuid4().hex
        headers = {
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary
        }

        producer = partial(
            self.multipart_producer,
            boundary,
            self.chat_id,
            caption,
            photo
        )
        await self.http_client.fetch(
            self.photo_url,
            method='POST',
            headers=headers,
            body_producer=producer,
        )

    async def send_log(self, date_str, identity, status='on'):
        """ Send a log message to a telegram chat via http post request

        :param date_str: date and time when a motion detection was
            turned on/off
        :type date_str: str
        :param identity: which camera changes the settings
        :type identity: str
        :param status: turned 'on' or 'off' - what actually happened
        :type status: str
        """
        text = '{} - {} - motion detection: {} #log'.format(
            date_str,
            identity,
            status
        )
        body = urlencode({'chat_id': self.chat_id, 'text': text})
        await self.http_client.fetch(self.message_url, method='POST', body=body)
