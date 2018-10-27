# -*- coding: utf-8 -*-

from ..base import BaseHandler


class ApiHandler(BaseHandler):
    """ Handler for API using """

    @property
    def notification_manager(self):
        return self.application.notification_manager

    def check_xsrf_cookie(self):
        """ Don't verify _xsrf when token-based access is using """

        pass
