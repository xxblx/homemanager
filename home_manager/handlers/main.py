import os.path
import tornado.web
from .base import BaseHandler


class MainPageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        cameras = [
            (k, os.path.basename(self.cameras[k]['path_video']))
            for k in self.cameras
        ]
        self.render('index.html', cameras=cameras)
