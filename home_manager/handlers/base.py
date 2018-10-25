# -*- coding: utf-8 -*-

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

    @property
    def path_restrictions(self):
        return self.application.path_restrictions

    @tornado.concurrent.run_on_executor
    def verify_password(self, passwd, passwd_hash):
        return bcrypt.checkpw(passwd, passwd_hash)

    def get_current_user(self):
        return self.get_secure_cookie('username')
