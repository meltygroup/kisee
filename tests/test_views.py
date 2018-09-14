import pytest

import kisee.kisee as kisee
import mocks


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
    assert response.status == 400


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
    response = await client.post(
        "/users/",
        json={"username": "user", "email": "lol@lol.com", "password": "passwod"},
    )
    assert response.status == 201


async def test_post_users__conflict__user_already_exists(client, monkeypatch):
    monkeypatch.setattr(
        "kisee.providers.test.TestBackend.register_user", mocks.register_user
    )
    response = await client.post(
        "/users/",
        json={"username": "user", "password": "password", "email": "test@example.com"},
    )
    assert response.status == 409


async def test_get_forgotten_password(client):
    response = await client.get("/forgotten_passwords/")
    assert response.status == 200


async def test_post_forgotten_password(client, monkeypatch):
    monkeypatch.setattr("kisee.views.send_mail", mocks.send_mail)
    response = await client.post(
        "/forgotten_passwords/", json={"email": "foo@example.com"}
    )
    assert response.status == 201


async def post_forgotten_passwords__bad_request(client):
    """Bad request because missing either 'email' or 'username' field
    """
    response = await client.post(
        "/forgotten_passwords/", json={"some-useless-field": "foo"}
    )
    assert response.status == 400


async def test_post_users__bad_request__missing_required_fields(client):
    response = await client.post("/users/", json={"username": "only-username"})
    assert response.status == 400


async def test_post_users__bad_request__invalid_email(client):
    response = await client.post(
        "/users/", json={"username": "user", "email": "lol", "password": "passwod"}
    )
    assert response.status == 400


async def test_patch_users(client):
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json={"password": "passwod"},
    )
    assert response.status == 204


async def test_patch_users__bad_request__missing_field(client):
    """Missing 'password' field in json input
    """
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json={"some-useless-field": "foo"},
    )
    assert response.status == 400


async def test_post_password__can_not_authentify(client):
    response = await client.post(
        "/password/?change",
        json={"login": "foo", "password": "bar", "new-password": "new-password"},
    )
    assert response.status == 403


async def test_post_password__bad_request(client):
    """Missing required fields
    """
    response = await client.post("/password/?change", json={"login": "foo"})
    assert response.status == 400


async def test_post_password__missing_query_string(client):
    """Missing required fields
    """
    response = await client.post(
        "/password/",
        json={"login": "foo", "password": "bar", "new-password": "new-password"}
    )
    assert response.status == 400


async def test_health(client):
    response = await client.get("/health/")
    assert response.status == 200
