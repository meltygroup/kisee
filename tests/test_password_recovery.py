async def test_get_password_recoveries(client):
    response = await client.get("/password_recoveries/")
    assert response.status == 200


async def test_post_password_recoveries_wrong_username(client):
    response = await client.post(
        "/password_recoveries/", json={"email": "foo@example.com"}
    )
    assert response.status == 201  # Do not leak the info we don't have this email.


async def test_post_password_recoveries_good_username(client, monkeypatch):
    await client.app["identity_backend"].register_user(
        "foo@example.com", "bar", "foo@example.com"
    )
    response = await client.post(
        "/password_recoveries/", json={"email": "foo@example.com"}
    )
    assert response.status == 201


async def test_password_recoveries_with_token(client):
    await client.app["identity_backend"].register_user(
        "foo@example.com", "bar", "foo@example.com"
    )
    response = await client.post(
        "/password_recoveries/", json={"email": "foo@example.com"}
    )
    assert response.status == 201
    jwt = client.app["identity_backend"].password_reset_tokens.pop()
    response = await client.get(
        "/password_recoveries/", headers={"Authorization": "Bearer " + jwt},
    )
    body = await response.json()
    assert body["recover"]["url"]


async def test_post_password_recoveries_empty(client, monkeypatch):
    response = await client.post("/password_recoveries/", json={})
    assert response.status == 400


async def test_post_password_recoveries_by_username(client, monkeypatch):
    await client.app["identity_backend"].register_user("foo", "bar", "foo@example.com")
    response = await client.post("/password_recoveries/", json={"username": "foo"})
    assert response.status == 201


async def test_post_password_recoveries_by_login_for_backward_compatibility(
    client, monkeypatch
):
    await client.app["identity_backend"].register_user("foo", "bar", "foo@example.com")
    response = await client.post("/password_recoveries/", json={"login": "foo"})
    assert response.status == 201


async def test_post_password_recoveries__bad_request(client):
    """Bad request because missing either 'email' or 'username' field
    """
    response = await client.post(
        "/password_recoveries/", json={"some-useless-field": "foo"}
    )
    assert response.status == 400
