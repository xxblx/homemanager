import os
import asyncio

import tornado.web
import tornado.iostream
import tornado.httputil

from .base import WebAuthHandler


class VideoServeHandler(WebAuthHandler):
    chunk_size = 1024 * 1024  # 1 MiB
    directory_video = None

    def initialize(self, path_video):
        self.directory_video = os.path.dirname(path_video)

    @tornado.web.authenticated
    async def get(self, file_name, file_ext):
        # Check does file exist
        fpath = os.path.join(self.directory_video, file_name)
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
