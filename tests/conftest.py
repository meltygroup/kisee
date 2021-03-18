from datetime import datetime, timedelta

import jwt
import pytest

import kisee.kisee as kisee
from kisee.providers.demo import DemoBackend


@pytest.fixture
def backend():
    return DemoBackend({"username_min_len": 3})


@pytest.fixture
def settings():
    return kisee.load_conf("tests/test_settings.toml")


@pytest.fixture
def client(loop, aiohttp_client):
    settings = kisee.load_conf("tests/test_settings.toml")
    app = kisee.create_app(settings)
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def valid_jwt(settings):
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


@pytest.fixture
def valid_jwt_to_change_pwd(settings):
    return jwt.encode(
        {
            "iss": "Pouete",
            "password_reset_for": "toto",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "jti": "42",
        },
        settings["jwt"]["private_key"],
        algorithm="ES256",
    )
