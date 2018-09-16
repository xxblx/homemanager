# -*- coding: utf-8 -*-

from functools import wraps

import bcrypt
import tornado.web
import tornado.concurrent


class BaseHandler(tornado.web.RequestHandler):

    @property
    def loop(self):
        return self.application.loop

    @property
    def executor(self):
        return self.application.executor

    @property
    def db_pool(self):
        return self.application.db_pool

    @property
    async def db_conn(self):
        return self.db_pool.acquire()

    @property
    async def db_cur(self):
        return self.db_conn.cursor()

    @property
    def videos(self):
        return self.application.videos

    @property
    def videos_nums(self):
        return self.application.videos_nums

    @tornado.concurrent.run_on_executor
    def verify_password(self, passwd, passwd_hash):
        return bcrypt.checkpw(passwd, passwd_hash)

    def run_in_loop_executor(method):
        """ Decorator for queries to sqlite from Handlers """

        @wraps(method)
        async def wrapper(self, *args):
            future = self.loop.run_in_executor(None, method, self, *args)
            data = await future
            return data
        return wrapper

    def get_current_user(self):
        return self.get_secure_cookie('username')
