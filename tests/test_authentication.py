import base64
from datetime import datetime, timedelta
from types import SimpleNamespace

import aiohttp
import jwt
import pytest

from kisee import authentication, kisee
from kisee.authentication import _basic_authentication, _jwt_authentication
from kisee.identity_provider import ProviderError


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
    )


async def test_jwt_authentication_fails(settings, backend):
    """Assert that a random string is never a valid token.
    """
    s = b"foobar"
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        await _jwt_authentication(s, backend, settings["jwt"]["public_key"])


async def test_jwt_authentication_succeed(settings, valid_token, backend):
    await backend.register_user("toto", "toto", "toto", "toto@example.com")
    user, claims = await _jwt_authentication(
        valid_token, backend, settings["jwt"]["public_key"]
    )
    assert user.username == "toto"


async def test_basic_authentication_fails(backend):
    """Assert that a random string is never a valid basic auth.
    """
    s = b"foobar"
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        await _basic_authentication(s, backend)


async def test_malformed_basic_authentication_fails(backend):
    """Assert that a random string encoded in base64 is never a valid basic auth.
    """
    s = base64.b64encode(b"foobar")
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        await _basic_authentication(s, backend)


async def test_basic_authentication_succeed(backend):
    await backend.register_user("toto", "toto", "toto", "toto@example.com")
    user, claims = await _basic_authentication(base64.b64encode(b"toto:toto"), backend)
    assert user.username == "toto"


async def test_basic_authentication_bad_password(backend):
    await backend.register_user("toto", "toto", "toto", "toto@example.com")
    with pytest.raises(aiohttp.web_exceptions.HTTPUnauthorized):
        user, claims = await _basic_authentication(base64.b64encode(b"toto:t"), backend)


async def test_register_user_username_too_short(backend):
    with pytest.raises(ProviderError):
        await backend.register_user("to", "toto", "toto@example.com")


async def test_basic_authentication_no_user(backend):
    with pytest.raises(ValueError):
        await backend.identify(None, None)


@pytest.fixture
def fake_request(settings, valid_token):
    fake_request = SimpleNamespace()
    fake_request.headers = {"Authorization": "Bearer " + valid_token}
    fake_request.app = {"settings": settings}
    return fake_request


async def test_authenticate_user_jwt(fake_request, backend):
    fake_request.app["identity_backend"] = backend
    await backend.register_user("toto", "toto", "toto", "toto@example.com")
    user, claims = await authentication.authenticate_user(fake_request)
    assert user.username == "toto"


async def test_authenticate_user_bad_jwt(fake_request, backend):
    fake_request.app["identity_backend"] = backend
    await backend.register_user("tata", "tata", "tata", "tata@example.com")
    with pytest.raises(aiohttp.web.HTTPUnauthorized):
        user, claims = await authentication.authenticate_user(fake_request)
