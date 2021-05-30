import os
from concurrent.futures import ThreadPoolExecutor

import aiopg
import tornado.web

from .handlers.auth import LoginHandler, LogoutHandler
from .handlers.main import MainPageHandler
from .handlers.camera import CameraHandler
from .handlers.video import VideoServeHandler

from .handlers.api.router import UserStatusHandler
from .handlers.api.camera import MotionHandler, SetupHandler

from .notifications.manager import NotificationManager

from .sql_new.select import SelectQueries

from .conf import DSN, DEBUG, WORKERS, MAC_KEY, COOKIE_SECRET


class WebApp(tornado.web.Application):
    def __init__(self, loop, db_pool, cameras):
        self.loop = loop  # tornado wrapper for asyncio loop
        self.pool_executor = ThreadPoolExecutor(max_workers=WORKERS)
        self.db_pool = db_pool
        self.mac_key = MAC_KEY
        self.notification_manager = NotificationManager(loop)
        self.cameras_setup = {}

        handlers = [
            (r'/', MainPageHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/api/router/status/user', UserStatusHandler),
            (r'/api/camera/motion', MotionHandler),
            (r'/api/camera/setup', SetupHandler)
        ]

        self.cameras = {}
        for camera in cameras:
            self.cameras[camera[0]] = dict(
                zip(['device_name', 'path_video', 'path_activation'], camera)
            )
            # Web page
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
    :return: connection_pool, list of video sources, accesses list
    """
    db_pool = await aiopg.create_pool(dsn=DSN)
    async with await db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(SelectQueries.cameras)
            cameras = await cur.fetchall()

    return db_pool, cameras
