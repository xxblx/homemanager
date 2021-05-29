
import nacl.pwhash
import tornado.web
import tornado.concurrent


class BaseHandler(tornado.web.RequestHandler):

    @property
    def loop(self):
        return self.application.loop

    @property
    def pool_executor(self):
        return self.application.pool_executor

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
    def path_units_files(self):
        return self.application.path_units_files

    @property
    def path_restrictions(self):
        return self.application.path_restrictions

    async def check_password_hash(self, hashed, password):
        """ Compare entered password with exist password hash
        :param hashed: a hash of a password
        :type hashed: bytes
        :param password: a password entered by a user
        :type password: bytes
        :return: False if the password is wrong, otherwise - True
        """
        try:
            return await self.loop.run_in_executor(
                self.pool_executor,
                nacl.pwhash.verify,
                hashed,
                password
            )
        except nacl.exceptions.InvalidkeyError:
            return False

    def get_current_user(self):
        return self.get_secure_cookie('username')
