import pytest

import kisee.kisee as kisee


@pytest.fixture
def client(loop, aiohttp_client):
    settings = kisee.load_conf("tests/test_settings.toml")
    app = kisee.identification_app(settings)
    return loop.run_until_complete(aiohttp_client(app))


async def test_identification_app(client):
    response = await client.get("/")
    assert response.status == 200


async def test_post_jwt(client):
    response = await client.post(
        "/jwt/", json={"login": "test@localhost.com", "password": "tamtam"}
    )
    assert response.status == 201
    response = await client.post("/jwt/", json={"login": "test@localhost.com"})
    assert response.status == 422


async def test_post_jwt_bad_json(client):
    response = await client.post(
        "/jwt/", data=b"{", headers={"Content-Type": "application/json"}
    )
    assert response.status == 422


async def test_post_jwt_bad_password(client):
    """The test backend consider passwords of less than 4 chars to be wrong.
    """
    response = await client.post(
        "/jwt/", json={"login": "test@localhost.com", "password": ""}
    )
    assert response.status == 403


async def test_get_jwts(client):
    response = await client.get("/jwt/")
    assert response.status == 200


async def test_get_jwt(client):
    response = await client.get("/jwt/xxx")
    assert response.status == 500


async def test_get_users(client):
    response = await client.get("/users/")
    assert response.status == 200


async def test_post_users(client):
    response = await client.post("/users/", json={"username": "user", "password": "passwod"})
    assert response.status == 201

async def test_health(client):
    response = await client.get("/health/")
    assert response.status == 200
