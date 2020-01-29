import pytest

import kisee.kisee as kisee


@pytest.fixture
def client(loop, aiohttp_client):
    settings = kisee.load_conf("tests/test_settings.toml")
    app = kisee.create_app(settings)
    return loop.run_until_complete(aiohttp_client(app))


async def test_bad_json(client):
    response = await client.request(
        "POST",
        "/users/",
        data=b'{"username" "my_username"}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status == 400
