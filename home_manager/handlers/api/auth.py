# -*- coding: utf-8 -*-

from .base import ApiHandler
from ...sql import SELECT

import tornado.web


class TokenAuthHandler(ApiHandler):

    async def prepare(self):
        self.current_user = None

        try:
            token = self.get_argument('token')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(403, 'invalid token')

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SELECT['tokens'], (token,))
                res = await cur.fetchall()

        if not res:
            raise tornado.web.HTTPError(403, 'invalid token')

        self.current_user = {'identity': res[0][0]}
