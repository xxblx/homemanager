from urllib.parse import urljoin, urlencode
from tornado.httputil import url_concat
from datetime import datetime
from functools import partial
from time import mktime
from uuid import uuid4

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


async def multipart_producer(boundary, params, pic_data, write):
    boundary_bytes = boundary.encode()
    # params
    for key, value in params.items():
        if not isinstance(value, str):
            value = str(value)
        await write(
            (b'--%s\r\n' % boundary_bytes) +
            (b'Content-Disposition: form-data; name="%s"\r\n\r\n%s'
                % (key.encode(), value.encode())
            )
            + b'\r\n'
        )
    # picture
    await write(
        (b'--%s\r\n' % boundary_bytes) +
        b'Content-Disposition: form-data; name="pic"; filename="pic"\r\n'
        + b'Content-type: image/jpeg\r\n'
        + b'\r\n'
    )
    await write(pic_data)
    await write(b'\r\n')
    await write(b'--%s--\r\n' % (boundary_bytes,))


async def fetch(http_client, base_url, path, method, params=None):
    parameters = {
        'method': method,
        'raise_error': False,
        'request': urljoin(base_url, path)
    }
    if method in ('GET', 'DELETE'):
        if params:
            parameters['request'] = url_concat(urljoin(base_url, path), params)
    elif method == 'POST':
        parameters['body'] = urlencode(params)
    elif method == 'PUT':
        if params:
            parameters['request'] = url_concat(urljoin(base_url, path), params)
        # Workaround `ValueError: Body must not be None for method PUT`
        parameters['body'] = ''
    return await http_client.fetch(**parameters)


async def upload_picture(http_client, base_url, pic_data, params, method):
    boundary = uuid4().hex
    headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
    producer = partial(multipart_producer, boundary, params, pic_data)
    return await http_client.fetch(
        urljoin(base_url, PATH['motion']),
        method=method,
        headers=headers,
        body_producer=producer,
        raise_error=False
    )


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
