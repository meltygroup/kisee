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


async def test_post_users__bad_request__missing_required_fields(client):
    response = await client.post("/users/", json={"username": "only-username"})
    assert response.status == 400


async def test_post_users__bad_request__invalid_email(client):
    response = await client.post(
        "/users/", json={"username": "user", "email": "lol", "password": "passwod"}
    )
    assert response.status == 400
