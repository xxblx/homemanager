from urllib.parse import urljoin, urlencode
from tornado.httputil import url_concat
from datetime import datetime
from time import mktime

import json
import pytest
import tornado.ioloop

from db_manage import add_camera, add_router, add_session_token, delete_device
from homemanager.app import WebApp, init_db

PATH = {
    'new_tokens': '/api/tokens/new',
    'update_user_status': '/api/router/status/user',
    'motion': '/api/camera/motion',
    'setup': '/api/camera/setup'
}


async def fetch(http_client, base_url, path, method, params=None):
    parameters = {'method': method, 'raise_error': False}
    if method in ('GET', 'DELETE'):
        parameters['request'] = url_concat(urljoin(base_url, path), params)
    elif method == 'POST':
        parameters['request'] = urljoin(base_url, path)
        parameters['body'] = urlencode(params)
    elif method == 'PUT':
        parameters['request'] = url_concat(urljoin(base_url, path), params)
        # Workaround `ValueError: Body must not be None for method PUT`
        parameters['body'] = ''
    return await http_client.fetch(**parameters)


async def get_tokens(http_client, base_url, device):
    token_session = add_session_token(device, True)
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'POST',
                    params={'token_session': token_session})
    r_dct = json.loads(r.body)
    return {k: r_dct[k] for k in ('token_select', 'token_verify')}


@pytest.fixture
def router():
    router_name = 'router_{}'.format(int(mktime(datetime.utcnow().timetuple())))
    add_router(router_name)
    yield router_name
    delete_device(router_name)


@pytest.fixture
def camera():
    camera_name = 'camera_{}'.format(int(mktime(datetime.utcnow().timetuple())))
    add_camera(camera_name, '/homemanager/video-test/video.m3u8',
               '/homemanager/video-test/{}_activation'.format(camera_name))
    yield camera_name
    delete_device(camera_name)


@pytest.fixture
def app():
    loop = tornado.ioloop.IOLoop.current()
    db_pool, cameras = loop.asyncio_loop.run_until_complete(init_db())
    return WebApp(loop.asyncio_loop, db_pool, cameras)
