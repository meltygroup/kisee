from kisee import kisee
import base64
from datetime import datetime, timedelta
import pytest
import aiohttp
import jwt

from kisee.providers.demo import DemoBackend
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


async def test_jwt_authentication_fails(settings):
    """Assert that a random string is never a valid token.
    """
    s = b"foobar"
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        await _jwt_authentication(s, DemoBackend(), settings["jwt"]["public_key"])


async def test_jwt_authentication_succeed(settings, valid_token):
    async with DemoBackend() as backend:
        await backend.register_user("toto", "toto", "toto", "toto@example.com")
        user, claims = await _jwt_authentication(
            valid_token, backend, settings["jwt"]["public_key"]
        )

    assert user.username == "toto"


async def test_basic_authentication_fails():
    """Assert that a random string is never a valid basic auth.
    """
    s = b"foobar"
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        await _basic_authentication(s, DemoBackend())


async def test_basic_authentication_succeed():
    async with DemoBackend() as backend:
        await backend.register_user("toto", "toto", "toto", "toto@example.com")
        user, claims = await _basic_authentication(
            base64.b64encode(b"toto:toto"), backend
        )
    assert user.username == "toto"


async def test_basic_authentication_bad_password():
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        user, claims = await _basic_authentication(
            base64.b64encode(b"toto:t"), DemoBackend()
        )
