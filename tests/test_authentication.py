from kisee import kisee
import base64
from datetime import datetime, timedelta
import pytest
import asyncio
import aiohttp
import jwt
from kisee.providers.demo import DemoBackend
from hypothesis import given
from hypothesis.strategies import text, binary

from kisee.authentication import _jwt_authentication, _basic_authentication


@pytest.fixture
def settings():
    return kisee.load_conf("tests/test_settings.toml")


@pytest.fixture
def valid_token(settings):
    return jwt.encode(
        {
            "iss": "Pouete",
            "sub": "toto",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "jti": "42",
        },
        settings["jwt"]["private_key"],
        algorithm="ES256",
    ).decode("utf8")


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@given(text())
def test_jwt_authentication_fails(settings, s):
    """Assert that a random string is never a valid token.
    """
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        run(_jwt_authentication(s, DemoBackend(), settings["jwt"]["public_key"]))


def test_jwt_authentication_succeed(settings, valid_token):
    user, claims = run(
        _jwt_authentication(valid_token, DemoBackend(), settings["jwt"]["public_key"])
    )
    assert user.username == "toto"


@given(binary())
def test_basic_authentication_fails(s: bytes):
    """Assert that a random string is never a valid basic auth.
    """
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        run(_basic_authentication(s, DemoBackend()))


def test_basic_authentication_succeed():
    user, claims = run(
        _basic_authentication(base64.b64encode(b"toto:toto"), DemoBackend())
    )
    assert user.username == "toto"


def test_basic_authentication_bad_password():
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        user, claims = run(
            _basic_authentication(base64.b64encode(b"toto:t"), DemoBackend())
        )
