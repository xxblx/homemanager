import tornado.web

from ...sql_new.update import UpdateQueries
from .base import ApiHandler


class UserStatusHandler(ApiHandler):
    @tornado.web.authenticated
    async def post(self):
        user_id = self.get_argument('user_id')
        status = self.get_argument('status')
        if int(status) == 1:
            status = True
        else:
            status = False
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(UpdateQueries.user_status, (status, user_id))
