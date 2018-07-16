import pytest
import shapeidp.kisee as kisee


@pytest.fixture
def client(loop, aiohttp_client):
    settings = kisee.load_conf("tests/test_settings.toml")
    app = kisee.identification_app(settings)
    return loop.run_until_complete(aiohttp_client(app))


async def test_identification_app(client):
    response = await client.get("/")
    assert response.status == 200


async def test_post_jwt(client):
    response = await client.post("/jwt/", json={
        "login": "test@localhost.com",
        "password": "tamtam"
    })
    assert response.status == 200
    response = await client.post("/jwt/", json={
        "login": "test@localhost.com"
    })
    assert response.status == 422


async def test_get_jwts(client):
    response = await client.get("/jwt/")
    assert response.status == 200


async def test_get_jwt(client):
    response = await client.get("/jwt/xxx")
    assert response.status == 500
