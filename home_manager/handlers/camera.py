import os.path
import tornado.web
from .base import BaseHandler


class CameraHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        camera_name = self.request.path.strip('/').split('/')[-1]
        cameras = [
            (k, os.path.basename(self.cameras[k]['path_video']))
            for k in self.cameras
        ]
        idx = [i for i in range(len(cameras)) if cameras[i][0] == camera_name]
        idx = idx[0]
        self.render('camera.html', idx=idx, cameras=cameras)
