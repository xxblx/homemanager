
from datetime import datetime, timedelta
from uuid import uuid1, uuid4

import tornado.web

from .base import BaseApiHandler
from ...sql_new.select import SelectQueries
from ...sql_new.insert import InsertQueries
from ...sql_new.delete import DeleteQueries


class BaseTokensHandler(BaseApiHandler):
    @property
    def token_expires_time(self):
        return self.application.token_expires_time

    async def generate_tokens(self, device_id, permanent=False):
        """ Generate three new tokens for a user with given username:
            * select_token used in select queries in db.
            * verify_token used for verification of select and renew tokens.
                verify_token isn't stored directly in db. Instead of that
                hash of the token stored. In case of unexpected read access
                to db (e.g. theft of db dump, injection, etc) plain
                verify_token isn't going to be compromised, it makes
                all stolen tokens useless because only the app knows mac key
                used for hashing and the app always hashes the content of
                the verify_token argument of post request.
            * renew_token used for one-time issuing new three tokens.
        :return: a dict with tokens
        """
        token_verify = uuid4().hex
        token_renew = uuid4().hex
        # Generate unique int value based on the clock
        # Right shift by 64 likely deletes MAC from uuid1
        token_select = int.from_bytes(
            uuid1().bytes, byteorder='big', signed=True
        ) >> 64
        # token_verify stored as a hash in db instead of plain-text
        token_verify_hash = await self.hash_token(token_verify)
        if permanent:
            expires_in = None
        else:
            expires_in = datetime.now() + \
                         timedelta(seconds=self.token_expires_time)

        args = (device_id, token_select, token_verify_hash, token_renew,
                expires_in)
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(InsertQueries.tokens, args)
                res = await cur.fetchall()
        tokens = {
            'token_select': token_select,
            'token_verify': token_verify,
            'token_renew': token_renew,
            'expires_in': res[0][0]
        }
        return tokens


class ApiTokensNewHandler(BaseTokensHandler):
    async def post(self):
        try:
            token_session = self.get_argument('token_session')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(400)

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.token_session, (token_session,))
                res = await cur.fetchall()
        if not res:
            raise tornado.web.HTTPError(403, 'invalid token')

        tokens = await self.generate_tokens(*res[0])
        # Delete used token_session
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(DeleteQueries.token_session, (token_session,))

        self.write(tokens)


class ApiTokensRenewHandler(BaseTokensHandler):
    # TODO
    pass
