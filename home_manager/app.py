# -*- coding: utf-8 -*-

import os
from concurrent.futures import ThreadPoolExecutor

import aiopg
import tornado.web

from .handlers.auth import LoginHandler, LogoutHandler
from .handlers.main import MainPageHandler, SourcePageHandler
from .handlers.video import VideoServeHandler

from .handlers.api.main import PersonHandler, MotionHandler

from .sql import SELECT

from .conf import DSN, DEBUG


class WebApp(tornado.web.Application):
    def __init__(self, loop, db_pool, videos, access_list):
        self.loop = loop  # tornado wrapper for asyncio loop
        self.executor = ThreadPoolExecutor(4)
        self.db_pool = db_pool

        self.videos = videos
        self.videos_nums = set(v[0] for v in self.videos)

        self.path_restrictions = {
            v[1]: {'id': v[0], 'name': v[2]} for v in access_list
        }

        handlers = [
            (r'/', MainPageHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/source/([0-9]*/?)', SourcePageHandler),
            (r'/api/person', PersonHandler),
            (r'/api/motion', MotionHandler)
        ]

        # Add video paths to handlers
        for video in self.videos:
            path = os.path.dirname(video[1])
            handlers.append(
                (r'/video/%d/(video[0-9]?\.(m3u8|ts))' % video[0],
                 VideoServeHandler, {'dir_path': path})
            )

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        static_path = os.path.join(os.path.dirname(__file__), 'static')

        settings = {
            'template_path': template_path,
            'static_path': static_path,
            'login_url': '/login',
            'debug': DEBUG,
            'xsrf_cookies': True,
            'cookie_secret': os.urandom(32)
        }

        super(WebApp, self).__init__(handlers, **settings)


async def init_db():
    db_pool = await aiopg.create_pool(dsn=DSN)

    async with await db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(SELECT['video'])
            videos = await cur.fetchall()

            await cur.execute(SELECT['access'])
            access_list = await cur.fetchall()

    return db_pool, videos, access_list
