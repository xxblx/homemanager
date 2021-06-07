import os.path
import tornado.web

from .base import WebAuthHandler
from ..sql_new.select import SelectQueries


class MainPageHandler(WebAuthHandler):
    @tornado.web.authenticated
    async def get(self):
        cameras = []
        res = await self.db_fetch(SelectQueries.cameras_detailed)
        if res:
            for _cam in res['data']:
                camera = list(_cam)
                camera[1] = os.path.basename(camera[1])
                cameras.append(camera)
        self.render('index.html', cameras=cameras)
