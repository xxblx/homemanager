import pytest

from .base import PATH, fetch, get_tokens, upload_picture, app, camera


@pytest.mark.gen_test
async def test_camera_setup(http_client, base_url, camera):
    tokens = await get_tokens(http_client, base_url, camera)
    r = await fetch(http_client, base_url, PATH['setup'], 'GET', params=tokens)
    assert r.code == 200

    # Camera doesn't have permission to the path if method != GET
    r = await fetch(http_client, base_url, PATH['setup'], 'POST', params=tokens)
    assert r.code == 401

    # Wrong tokens
    tokens['token_select'] = 123
    r = await fetch(http_client, base_url, PATH['setup'], 'GET', params=tokens)
    assert r.code == 403

    # Without tokens
    r = await fetch(http_client, base_url, PATH['setup'], 'GET')
    assert r.code == 403


@pytest.mark.gen_test
async def test_camera_motion(http_client, base_url, camera):
    tokens = await get_tokens(http_client, base_url, camera)
    with open('/homemanager/motion-test/pic.jpg', 'rb') as f:
        pic_data = f.read()
    r = await upload_picture(http_client, base_url, pic_data, params=tokens,
                             method='POST')
    assert r.code == 200
    # Wrong tokens
    tokens['token_select'] = 123
    r = await upload_picture(http_client, base_url, pic_data, params=tokens,
                             method='POST')
    assert r.code == 403
    # Without tokens
    tokens['token_select'] = 123
    r = await upload_picture(http_client, base_url, pic_data, params=dict(),
                             method='POST')
    assert r.code == 403


@pytest.mark.gen_test
async def test_camera_wrong_role(http_client, base_url, camera):
    tokens = await get_tokens(http_client, base_url, camera)
    params = {'user_id': 1, 'status': 1}
    # Without tokens
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'POST',
                    params=params)
    assert r.code == 403
    # With tokens
    params.update(tokens)
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'POST',
                    params=params)
    assert r.code == 401
