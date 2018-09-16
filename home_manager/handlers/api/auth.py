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

        # Check does path have access restrictions
        path = self.request.path.split()[-1]
        if path in self.path_restrictions:
            select_key = 'access_tokens'
            args = (token, self.path_restrictions[path]['id'])
        else:
            select_key = 'tokens'
            args = (token,)

        # Select identity from db by token
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SELECT[select_key], args)
                res = await cur.fetchall()

        if not res:
            raise tornado.web.HTTPError(403, 'invalid token')

        self.current_user = {'identity': res[0][0]}
