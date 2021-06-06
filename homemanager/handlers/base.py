
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
        res = await self.db_fetch(SelectQueries.user_passwd, (username,))
        check = False
        if res:
            check = await self.check_password_hash(
                res['data'][0][0].tobytes(),
                tornado.escape.utf8(password)
            )
        return check

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

    async def _execute_sql(self, query, fetch=True, args=None):
        results = None
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                if fetch:
                    data = await cur.fetchall()
                    if data:
                        results = {
                            'data': data,
                            'columns': [i.name for i in cur.description]
                        }
        return results

    async def db_fetch(self, query, args=None):
        return await self._execute_sql(query, fetch=True, args=args)

    async def db_execute(self, query, args=None):
        return await self._execute_sql(query, fetch=False, args=args)


class WebAuthHandler(BaseHandler):
    def get_current_user(self):
        return self.get_secure_cookie('username')
