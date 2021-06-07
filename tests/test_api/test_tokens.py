from uuid import uuid4
import pytest

from .base import PATH, fetch, app, router
from db_manage import add_session_token


@pytest.mark.gen_test
async def test_tokens_new(http_client, base_url, router):
    token_session = add_session_token(router, True)

    # Wrong method with valid token
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'GET',
                    params={'token_session': token_session})
    assert r.code == 405

    # Valid token and correct method
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'POST',
                    params={'token_session': token_session})
    assert r.code == 200

    # Try to reuse token_session
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'POST',
                    params={'token_session': token_session})
    assert r.code == 403

    # Invalid token
    r = await fetch(http_client, base_url, PATH['new_tokens'], 'POST',
                    params={'token_session': uuid4().hex})
    assert r.code == 403
