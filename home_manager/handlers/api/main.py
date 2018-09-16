# -*- coding: utf-8 -*-

from time import mktime
from datetime import datetime

import tornado.web

from ...sql import SELECT, UPDATE, INSERT
from .auth import TokenAuthHandler


class PersonHandler(TokenAuthHandler):
    # TODO: split access from different tokens
    @tornado.web.authenticated
    async def get(self):
        username_id = self.get_argument('username_id')
        status = self.get_argument('status')

        if int(status) == 1:
            status = True
        else:
            status = False

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(UPDATE['status'], (status, username_id))


class MotionHandler(TokenAuthHandler):
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
