import os
import asyncio

import tornado.web
import tornado.iostream
import tornado.httputil

from .base import BaseHandler


class VideoServeHandler(BaseHandler):
    """ Class for aserving videofiles for authenticated users """

    chunk_size = 1024 * 1024  # 1 MiB

    def initialize(self, dir_path):
        self.dir_path = dir_path

    @tornado.web.authenticated
    async def get(self, file_name, file_ext):
        fpath = os.path.join(self.dir_path, file_name)

        # Check does file exist
        if not os.path.exists(fpath):
            raise tornado.web.HTTPError(404)
        elif not os.path.isfile(fpath):
            raise tornado.web.HTTPError(403)

        # Headers
        if file_ext == 'm3u8':
            content_type = 'application/vnd.apple.mpegurl'
        else:
            content_type = 'video/mp2t'

        self.set_header('Content-Length', os.stat(fpath).st_size)
        self.set_header('Content-Type', content_type)

        with open(fpath, 'rb') as video_file:
            while True:
                chunk = video_file.read(self.chunk_size)
                if not chunk:
                    break

                try:
                    self.write(chunk)
                    await self.flush()
                # If client has closed the connection
                except tornado.iostream.StreamClosedError:
                    break
                finally:
                    del chunk
                    # Prevent blocking
                    await asyncio.sleep(0)
