import pytest
import jwt
import kisee.kisee as kisee
from datetime import datetime, timedelta


@pytest.fixture
def settings():
    return kisee.load_conf("tests/test_settings.toml")


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
    ).decode("utf8")


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
    ).decode("utf8")


@pytest.fixture
def client(loop, aiohttp_client):
    settings = kisee.load_conf("tests/test_settings.toml")
    app = kisee.create_app(settings)
    return loop.run_until_complete(aiohttp_client(app))


async def test_create_app(client):
    response = await client.get("/")
    assert response.status == 200


async def test_post_jwt(client):
    await client.app["identity_backend"].register_user(
        "test@example.com", "tamtam", "test@example.com",
    )
    response = await client.post(
        "/jwt/", json={"username": "test@example.com", "password": "tamtam"}
    )
    assert response.status == 201
    response = await client.post("/jwt/", json={"username": "test@localhost.com"})
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
        "/jwt/", json={"username": "test@localhost.com", "password": ""}
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
    # Try again, should conflict
    response = await client.post(
        "/users/",
        json={"username": "user", "email": "lol@lol.com", "password": "passwod"},
    )
    assert response.status == 409


async def test_post_users_login_too_short(client):
    response = await client.post(
        "/users/",
        json={"username": "u", "email": "lol@lol.com", "password": "passwod"},
    )
    assert response.status == 400


async def test_post_bad_json_to_users(client):
    response = await client.post(
        "/users/", headers={"Content-Type": "application/json"}, data=b"",
    )

    assert response.status == 400
    assert response.reason == "Malformed JSON"


async def test_post_users__conflict__user_already_exists(client):
    response = await client.post(
        "/users/",
        json={"username": "user", "password": "password", "email": "test@example.com"},
    )
    assert response.status == 201
    response = await client.post(
        "/users/",
        json={"username": "user", "password": "password", "email": "test@example.com"},
    )
    assert response.status == 409


async def test_get_forgotten_password(client):
    response = await client.get("/forgotten_passwords/")
    assert response.status == 200


async def test_post_forgotten_password_wrong_username(client):
    response = await client.post(
        "/forgotten_passwords/", json={"email": "foo@example.com"}
    )
    assert response.status == 201  # Do not leak the info we don't have this email.


async def test_post_forgotten_password_good_username(client, monkeypatch):
    await client.app["identity_backend"].register_user(
        "foo@example.com", "bar", "foo@example.com"
    )
    response = await client.post(
        "/forgotten_passwords/", json={"email": "foo@example.com"}
    )
    assert response.status == 201


async def test_post_forgotten_password_empty(client, monkeypatch):
    response = await client.post("/forgotten_passwords/", json={})
    assert response.status == 400


async def test_post_forgotten_password_by_username(client, monkeypatch):
    await client.app["identity_backend"].register_user("foo", "bar", "foo@example.com")
    response = await client.post("/forgotten_passwords/", json={"username": "foo"})
    assert response.status == 201


async def test_post_forgotten_password_by_login_for_backward_compatibility(
    client, monkeypatch
):
    await client.app["identity_backend"].register_user("foo", "bar", "foo@example.com")
    response = await client.post("/forgotten_passwords/", json={"login": "foo"})
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
    await client.app["identity_backend"].register_user(
        "test", "test", "foo@example.com"
    )
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json={"password": "passwod"},
    )
    assert response.status == 204


async def test_patch_unexisting_user_with_existing_jwt(client, valid_jwt):
    """Even with a valid JWT, if the user just does not exist, we can't
    use the JWT.
    """
    response = await client.patch(
        "/users/toto/",
        headers={"Authorization": "Bearer " + valid_jwt},
        json={"password": "passwod"},
    )
    assert response.status == 403
    assert response.reason == "Use a password lost token or basic auth."


async def test_patch_users_with_jwt(client, valid_jwt):
    """A normal JWT is not enough to change a password: it does not proove
    the user knows its password.

    To change a password, one must either have:
    - A password reset token (from "I forgot my password").
    - Auth using basic auth to proove it knows its password.
    """
    await client.app["identity_backend"].register_user("toto", "bar", "foo@example.com")

    response = await client.patch(
        "/users/toto/",
        headers={"Authorization": "Bearer " + valid_jwt},
        json={"password": "passwod"},
    )
    assert response.status == 403


async def test_patch_wrong_user_with_jwt(client, valid_jwt_to_change_pwd):
    await client.app["identity_backend"].register_user(
        "admin", "bar", "admin@example.com"
    )
    await client.app["identity_backend"].register_user(
        "toto", "bar", "pouette@example.com"
    )
    response = await client.patch(
        "/users/admin/",
        headers={"Authorization": "Bearer " + valid_jwt_to_change_pwd},
        json={"password": "passwod"},
    )
    assert response.status == 403
    assert "Token does not apply" in response.reason


async def test_patch_users_missing_auth(client):
    response = await client.patch("/users/test/", json={"password": "passwod"})
    assert response.status == 401


async def test_patch_users_bad_auth(client):
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "I AM ROOT TAHHTS IT"},
        json={"password": "passwod"},
    )
    assert response.status == 401


async def test_patch_users__bad_request__missing_field(client):
    """Missing 'password' field in json input
    """
    await client.app["identity_backend"].register_user(
        "test", "test", "foo@example.com"
    )
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json={"some-useless-field": "foo"},
    )
    assert response.status == 400


async def test_health(client):
    response = await client.get("/health/")
    assert response.status == 200
