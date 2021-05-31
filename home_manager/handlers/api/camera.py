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
from ...sql_new.update import UpdateQueries
from .base import ApiHandler


class ApiCameraHandler(ApiHandler):
    path_activation = None
    device_settings = None
    md_changed = False
    _settings_default = {
        'stream': False, 'motion_detection': False, 'night_mode': False
    }

    @staticmethod
    def check_night():
        """ Check is current time between sunrise and sunset """
        location = LocationInfo(**LOCATION)
        datetime_now = datetime.now(tz=location.tzinfo)
        sun_info = sun(location.observer, date=datetime_now.date(),
                       tzinfo=location.timezone)
        return sun_info['sunrise'] <= datetime_now < sun_info['sunset']

    async def check_active_users(self):
        res = await self.execute_query(SelectQueries.active_users)
        return bool(res['data'])

    async def prepare_settings(self):
        res = await self.execute_query(SelectQueries.camera_settings,
                                       args=(self.current_user['device_id'],))
        settings = dict(zip(res['columns'], res['data'][0]))
        self.path_activation = settings.pop('path_activation')
        _was_active = settings['motion_detection']

        if await self.check_active_users():
            settings = self._settings_default
        else:
            settings['stream'], settings['motion_detection'] = True, True
            if self.check_night():
                settings['night_mode'] = True

        self.md_changed = settings['motion_detection'] == _was_active
        self.device_settings = settings

    async def save_settings(self):
        await self.execute_query(UpdateQueries.camera_settings, args=(
            self.device_settings['stream'],
            self.device_settings['motion_detection'],
            self.device_settings['night_mode'],
            self.current_user['device_id']
            ), fetch=False
        )


class MotionHandler(ApiCameraHandler):
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


class SetupHandler(ApiCameraHandler):
    @tornado.web.authenticated
    async def get(self):
        await self.prepare_settings()
        # Use path to activate systemd service
        if self.device_settings['stream']:
            if not os.path.exists(self.path_activation):
                open(self.path_activation, 'a').close()
        else:
            if os.path.exists(self.path_activation):
                os.remove(self.path_activation)
        # Send notification
        if self.md_changed:
            status = 'on' if self.device_settings['motion_detection'] else 'off'
            await self.notification_manager.send_log(
                datetime.now(),
                self.current_user['device_name'],
                status
            )
        # Save and apply settings
        await self.save_settings()
        self.write(self.device_settings)
