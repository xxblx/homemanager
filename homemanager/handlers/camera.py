import os.path
import tornado.web

from .base import WebAuthHandler
from ..sql_new.select import SelectQueries


class CameraHandler(WebAuthHandler):
    @tornado.web.authenticated
    async def get(self):
        camera_name = self.request.path.strip('/').split('/')[-1]
        cameras = []
        idx = None
        res = await self.db_fetch(SelectQueries.cameras_detailed)
        if res:
            for i, _cam in enumerate(res['data']):
                if _cam[0] == camera_name:
                    idx = i
                camera = list(_cam)
                camera[1] = os.path.basename(camera[1])
                cameras.append(camera)
        self.render('camera.html', idx=idx, cameras=cameras)
