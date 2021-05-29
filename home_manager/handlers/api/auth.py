from .base import ApiHandler
from ...sql_new.select import SelectQueries

import tornado.web


class TokenAuthHandler(ApiHandler):
    """ Class for token based auth for api """

    async def prepare(self):
        self.current_user = None

        try:
            token = self.get_argument('token')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(403, 'invalid token')

        # Check does path have access restrictions
        path = self.request.path.split()[-1]
        if path in self.path_restrictions:
            query = SelectQueries.access_tokens
            args = (token, self.path_restrictions[path]['id'])
        else:
            query = SelectQueries.identity_token
            args = (token,)

        # Select identity from db by token
        # If path has retrictions but the token is not allowed for the path
        # the result would be empty
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                res = await cur.fetchall()

        if not res:
            raise tornado.web.HTTPError(403, 'invalid token')

        self.current_user = {'identity': res[0][0]}
