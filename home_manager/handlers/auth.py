import tornado.web

from ..sql_new.select import SelectQueries
from .base import BaseHandler

class LoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.redirect('/')
        else:
            self.render('login.html')

    async def post(self):
        username = self.get_argument('username')
        passwd = self.get_argument('passwd')

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.user_passwd, (username,))
                _res = await cur.fetchall()

        # If user doesn't exist
        if not _res:
            raise tornado.web.HTTPError(403, 'invalid username or password')

        # Check password
        passwd_hashed = _res[0][0].tobytes()
        passwd_check = await self.check_password_hash(
            passwd_hashed,
            tornado.escape.utf8(passwd)
        )
        if not passwd_check:
            raise tornado.web.HTTPError(403, 'invalid username or password')

        self.set_secure_cookie('username', username)
        self.redirect(self.get_argument('next', '/'))


class LogoutHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.clear_cookie('username')
        self.redirect(self.get_argument('next', '/'))
