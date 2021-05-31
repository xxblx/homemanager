from uuid import uuid4
import json
import pytest

from .base import PATH, fetch, app, router
from db_manage import add_session_token


@pytest.mark.gen_test
async def test_status_update(http_client, base_url, router):
    token_session = add_session_token(router, True)
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'POST',
                    params={'token_session': token_session})
    assert r.code == 200
    tokens = json.loads(r.body)
    params = {'user_id': 1, 'status': 1}
    params.update({k: tokens[k] for k in ('token_select', 'token_verify')})

    # Correct tokens and method
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'POST',
                    params=params)
    assert r.code == 200

    # GET won't work
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'GET',
                    params=params)
    assert r.code == 401

    # Wrong token
    params['token_verify'] = uuid4().hex
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'GET',
                    params=params)
    assert r.code == 403

    # Lack of mandatory parameters
    del params['user_id']
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'GET',
                    params=params)
    assert r.code == 403

    params['user_id'] = 1
    del params['token_select']
    r = await fetch(http_client, base_url, PATH['update_user_status'], 'GET',
                    params=params)
    assert r.code == 403


@pytest.mark.gen_test
async def test_router_wrong_role(http_client, base_url, router):
    token_session = add_session_token(router, True)
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'POST',
                    params={'token_session': token_session})
    tokens = json.loads(r.body)
    tokens = {k: tokens[k] for k in ('token_select', 'token_verify')}

    r = await fetch(http_client, base_url, PATH['setup'], 'GET',
                    params=tokens)
    assert r.code == 401
