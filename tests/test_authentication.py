from kisee import kisee
from datetime import datetime, timedelta
import pytest
import asyncio
import jwt
from kisee.providers.demo import DemoBackend
from hypothesis import given
from hypothesis.strategies import text

from kisee.authentication import jwt_authentication


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
    assert run(jwt_authentication(s, None, settings["jwt"]["public_key"])) is None


def test_jwt_authentication_succeed(settings, valid_token):
    assert (
        run(
            jwt_authentication(
                valid_token, DemoBackend(), settings["jwt"]["public_key"]
            )
        ).username
        == "toto"
    )
