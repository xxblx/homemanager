import tornado.web

from .base import WebAuthHandler


class LoginHandler(WebAuthHandler):
    def get(self):
        next_uri = self.get_argument('next', '/')
        if self.get_current_user():
            self.redirect(next_uri)
        else:
            self.set_secure_cookie('next', next_uri, expires_days=1)
            self.render('login.html')

    async def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        check = await self.check_user(username, password)
        if not check:
            raise tornado.web.HTTPError(403, 'invalid username or password')
        self.set_secure_cookie('username', username)

        next_uri = self.get_secure_cookie('next')
        if not next_uri:
            next_uri = '/'
        self.clear_cookie('next')
        self.redirect(next_uri)


class LogoutHandler(WebAuthHandler):
    def get(self):
        if self.get_current_user():
            self.clear_cookie('username')
        self.redirect('/')
