import os.path
import tornado.web
from .base import WebAuthHandler


class MainPageHandler(WebAuthHandler):
    @tornado.web.authenticated
    def get(self):
        cameras = [
            (k, os.path.basename(self.cameras[k]['path_video']))
            for k in self.cameras
        ]
        self.render('index.html', cameras=cameras)
