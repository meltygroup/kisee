import pytest

import kisee.kisee as kisee


@pytest.fixture
def client(loop, aiohttp_client):
    settings = kisee.load_conf("tests/test_settings.toml")
    app = kisee.create_app(settings)
    return loop.run_until_complete(aiohttp_client(app))
