import os
from concurrent.futures import ThreadPoolExecutor

import aiopg
import tornado.web

from .handlers.auth import LoginHandler, LogoutHandler
from .handlers.main import MainPageHandler
from .handlers.camera import CameraHandler
from .handlers.video import VideoServeHandler

from .handlers.api.tokens import ApiTokensNewHandler
from .handlers.api.router import UserStatusHandler
from .handlers.api.camera import MotionHandler, SetupHandler

from .notifications.manager import NotificationManager

from .sql.select import SelectQueries

from .conf import (DB_SETTINGS, DEBUG, WORKERS, MAC_KEY, COOKIE_SECRET,
                   TOKEN_EXPIRES_TIME)


class WebApp(tornado.web.Application):
    def __init__(self, loop, db_pool, cameras):
        self.loop = loop  # tornado wrapper for asyncio loop
        self.pool_executor = ThreadPoolExecutor(max_workers=WORKERS)
        self.db_pool = db_pool
        self.mac_key = MAC_KEY
        self.token_expires_time = TOKEN_EXPIRES_TIME
        self.notification_manager = NotificationManager(loop)

        handlers = [
            (r'/', MainPageHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/api/tokens/new', ApiTokensNewHandler),
            (r'/api/router/status/user', UserStatusHandler),
            (r'/api/camera/motion', MotionHandler),
            (r'/api/camera/setup', SetupHandler)
        ]

        for camera in cameras:
            # Camera page
            handlers.append((
                r'/camera/{}'.format(camera[0]), CameraHandler
            ))
            # Video file
            fname = os.path.splitext(os.path.basename(camera[1]))[0]
            handlers.append((
                r'/video/{}/({})'.format(
                    camera[0],  # camera name
                    fname+r'[0-9]?\.(m3u8|ts)'
                ),
                VideoServeHandler, {'path_video': camera[1]}
            ))

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = {
            'template_path': template_path,
            'static_path': static_path,
            'login_url': '/login',
            'debug': DEBUG,
            'xsrf_cookies': True,
            'cookie_secret': COOKIE_SECRET
        }
        super(WebApp, self).__init__(handlers, **settings)


async def init_db():
    """ Connect to database and get initial data
    :return: connection_pool, list of cameras
    """
    db_pool = await aiopg.create_pool(**DB_SETTINGS)
    async with await db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(SelectQueries.cameras)
            cameras = await cur.fetchall()

    return db_pool, cameras
