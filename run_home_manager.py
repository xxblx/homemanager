#!VENV/bin/python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop

from home_manager.app import WebApp, init_db
from home_manager.conf import HOST, PORT


def main():
    loop = tornado.ioloop.IOLoop.current()
    db_pool, videos, access_list = loop.asyncio_loop.run_until_complete(
        init_db()
    )
    app = WebApp(loop, db_pool, videos, access_list)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(PORT, HOST)

    try:
        loop.start()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
