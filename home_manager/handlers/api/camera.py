# -*- coding: utf-8 -*-

import base64

from time import mktime
from datetime import datetime

import tornado.web

from astral import Location

from ...conf import LOCATION
from ...sql import SELECT, INSERT
from .auth import TokenAuthHandler


class MotionHandler(TokenAuthHandler):
    """ Class for capturing motion pictures from cameras """

    @tornado.web.authenticated
    async def post(self):
        datetime_now = datetime.now()
        pic = self.request.files['pic'][0]

        if pic['content_type'] != 'image/jpeg':
            raise tornado.web.HTTPError(400)

        # Check does user at home
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SELECT['status'])
                res = await cur.fetchall()

        # Send notifications
        if not res:
            await self.notification_manager.send_notification(
                datetime_now,
                self.current_user['identity'],
                pic['body']
            )

        # Save base64 encoded photo in db
        pic_encoded = base64.encodebytes(pic['body'])
        now = mktime(datetime_now.utctimetuple())
        values = (pic_encoded, self.current_user['identity'], now)

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(INSERT['motion'], values)


class SetupHandler(TokenAuthHandler):
    """ Class for sharing setting to cameras """

    camera_settings = {'night_mode': 0, 'rtsp': 0, 'motion_detect': 0}

    def check_sun(self):
        """ Check is current time between sunrise and sunset """

        sun = Location(LOCATION).sun()
        _now = datetime.now(tz=sun['sunrise'].tzinfo)

        return sun['sunrise'] <= _now <= sun['sunset']

    async def get(self):

        # Check does user at home
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SELECT['status'])
                res = await cur.fetchall()

        # Turn on RTSP and motion detect if users are not at home
        camera_settings = self.camera_settings.copy()
        if not res:
            for k in ('rtsp', 'motion_detect'):
                camera_settings[k] = 1

            # Night mode depends on local time
            if not self.check_sun():
                camera_settings['night_mode'] = 1

        self.write(camera_settings)
