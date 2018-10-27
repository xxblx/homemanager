# -*- coding: utf-8 -*-

from functools import wraps


class BaseBackend:
    """ Base class for notifications backends """

    def run_in_loop_executor(method):
        """ Decorator for blocking operations """

        @wraps(method)
        async def wrapper(self, *args):
            future = self.loop.run_in_executor(None, method, self, *args)
            data = await future
            return data
        return wrapper
