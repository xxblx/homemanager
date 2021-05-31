import functools

from psycopg2.sql import SQL, Identifier
from nacl.bindings.utils import sodium_memcmp
import nacl.encoding
import nacl.hash
import tornado.escape
import tornado.web

from ..base import BaseHandler
from ...sql_new.select import SelectQueries


class BaseApiHandler(BaseHandler):
    @property
    def mac_key(self):
        return self.application.mac_key

    @property
    def notification_manager(self):
        return self.application.notification_manager

    def check_xsrf_cookie(self):
        """ Don't verify _xsrf when token-based access is using """
        pass

    async def hash_token(self, token):
        """ Get hash of a token
        :param token: token for hashing
        :type token: str
        :param mac_key: key for message authentication
        :type mac_key: bytes
        :return: hex encoded hash of the token
        :rtype: bytes
        """
        return await self.loop.run_in_executor(
            self.pool_executor,
            # functools.partial used to pass keyword arguments to function
            functools.partial(
                # function
                nacl.hash.blake2b,
                # keyword args
                data=tornado.escape.utf8(token),
                key=self.mac_key,
                encoder=nacl.encoding.HexEncoder
            )
        )

    async def check_token_verify(self, plain, hashed):
        """ Check given plain-text token with a hashed one
        :param plain: token_verify in plain text provided by user
        :type plain: str
        :param hashed: token_verify selected from db
        :type hashed: bytes
        :return: True if hashed_token equals hash of plain_token
        :rtype: bool
        """
        _hashed = await self.hash_token(plain)
        return await self.loop.run_in_executor(
            self.pool_executor, sodium_memcmp, hashed, _hashed
        )


class ApiHandler(BaseApiHandler):
    async def prepare(self):
        self.current_user = None
        try:
            token_select = self.get_argument('token_select')
            token_verify = self.get_argument('token_verify')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(403, 'invalid tokens')

        # Check tokens validity
        check_token = False
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.token_auth, (token_select,))
                res = await cur.fetchall()
        if res:
            device_id, device_name, token_verify_hashed = res[0]
            token_verify_hashed = token_verify_hashed.tobytes()
            if await self.check_token_verify(token_verify, token_verify_hashed):
                check_token = True
        if not check_token:
            raise tornado.web.HTTPError(403, 'invalid tokens')
        current_user = {
            'device_id': device_id,
            'device_name': device_name
        }

        # Check access to the path
        path = self.request.path.rstrip('/')
        method = Identifier('method_{}'.format(self.request.method.lower()))
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    SQL(SelectQueries.device_role).format(method_col=method),
                    (device_id, path)
                )
                res = await cur.fetchall()
        if not res:
            raise tornado.web.HTTPError(401)
        self.current_user = current_user
