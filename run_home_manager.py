#!/usr/bin/env python3

import tornado.httpserver
import tornado.ioloop

from homemanager.app import WebApp, init_db
from homemanager.conf import HOST, PORT


def main():
    loop = tornado.ioloop.IOLoop.current()
    db_pool, cameras = loop.asyncio_loop.run_until_complete(
        init_db()
    )
    app = WebApp(loop.asyncio_loop, db_pool, cameras)
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
