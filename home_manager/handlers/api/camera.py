# -*- coding: utf-8 -*-

from time import mktime
from datetime import datetime

import tornado.web

from ...sql import SELECT, INSERT
from .auth import TokenAuthHandler


class MotionHandler(TokenAuthHandler):
    """ Class for capturing motion pictures from cameras """

    @tornado.web.authenticated
    async def get(self):
        pic = self.get_argument('pic')

        async with self.db_cur:
            await self.db_cur.execute(SELECT['status'])
            res = await self.db_cur.fetchall()

        if not res:
            # TODO: send email and telegram message
            pass

        now = mktime(datetime.now().utctimetuple())
        values = (pic, self.current_user['identity'], now)

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(INSERT['motion'], values)
