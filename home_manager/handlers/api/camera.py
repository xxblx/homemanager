import os
import base64

from time import mktime
from datetime import datetime

import tornado.web

from astral import LocationInfo
from astral.sun import sun

from ...conf import LOCATION
from ...sql import INSERT
from ...sql_new.select import SelectQueries
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
                await cur.execute(SelectQueries.active_users)
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

    @property
    def cameras_setup(self):
        return self.application.cameras_setup

    @property
    def active_file(self):
        """ Get path of 'active' file in identity's directory

        :return: [:class:`str`] path to 'active' file
        """
        return self.path_units_files[self.current_user['identity']]

    def check_sun(self):
        """ Check is current time between sunrise and sunset

        :return: [`bool` `True` if current time between sunrise and sunset
        """
        location = LocationInfo(**LOCATION)
        datetime_now = datetime.now(tz=location.tzinfo)
        sun_info = sun(location.observer, date=datetime_now.date(),
                       tzinfo=location.timezone)
        return sun_info['sunrise'] <= datetime_now <= sun_info['sunset']

    async def get(self):
        # Check does user at home
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.active_users)
                res = await cur.fetchall()

        camera_settings = self.camera_settings.copy()

        # Turn on RTSP and motion detect if users are not at home
        if not res:
            # `ffmpeg-rtsp-hls.service` uses path-based activation
            if not os.path.exists(self.active_file):
                open(self.active_file, 'a').close()

            for k in ('rtsp', 'motion_detect'):
                camera_settings[k] = 1

            # Night mode depends on local time
            if not self.check_sun():
                camera_settings['night_mode'] = 1

        else:
            if os.path.exists(self.active_file):
                os.remove(self.active_file)

        if self.current_user['identity'] not in self.cameras_setup:
            self.cameras_setup[self.current_user['identity']] = camera_settings
        else:
            # If motion detection has been switched send a log message
            motion_detect = camera_settings['motion_detect']
            motion_detect_prev = self.cameras_setup[
                self.current_user['identity']
            ]['motion_detect']

            if motion_detect != motion_detect_prev:
                if motion_detect == 1:
                    status = 'on'
                else:
                    status = 'off'

                await self.notification_manager.send_log(
                    datetime.now(),
                    self.current_user['identity'],
                    status
                )

            # Save new settings
            self.cameras_setup[self.current_user['identity']].update(
                camera_settings
            )

        self.write(camera_settings)
