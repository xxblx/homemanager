
import nacl.pwhash
import tornado.web
import tornado.concurrent

from ..sql_new.select import SelectQueries


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
    def cameras(self):
        return self.application.cameras

    async def check_user(self, username, password):
        """ Check given username and password
        :param username: username
        :type username: str
        :param password: user's password
        :type password: str
        :return: True is user exists and password is correct,
            otherwise - False
        :rtype: bool
        """
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.user_passwd, (username,))
                _res = await cur.fetchall()

        _check = False
        if _res:
            _check = await self.check_password_hash(
                _res[0][0].tobytes(),
                tornado.escape.utf8(password)
            )
        return _check

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

    async def execute_query(self, query, fetch=True, args=None):
        results = None
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                if fetch:
                    results = {
                        'data': await cur.fetchall(),
                        'columns': [i.name for i in cur.description]
                    }
        return results


class WebAuthHandler(BaseHandler):
    def get_current_user(self):
        return self.get_secure_cookie('username')