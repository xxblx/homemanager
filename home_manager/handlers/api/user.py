import tornado.web

from ...sql import UPDATE
from .auth import TokenAuthHandler


class StatusHandler(TokenAuthHandler):
    """ Class for users statuses updates """

    @tornado.web.authenticated
    async def post(self):
        username_id = self.get_argument('username_id')
        status = self.get_argument('status')

        if int(status) == 1:
            status = True
        else:
            status = False

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(UPDATE['status'], (status, username_id))
