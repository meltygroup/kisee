async def test_patch_users(client):
    await client.app["identity_backend"].register_user(
        "test", "test", "foo@example.com"
    )
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json=[{"op": "replace", "path": "/password", "value": "passwod"}],
    )
    assert response.status == 204


async def test_patch_wrong_field(client):
    """We currently only support patching password, let be explicit when
    someone tries to patch something else.
    """
    await client.app["identity_backend"].register_user(
        "test", "test", "foo@example.com"
    )
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json=[{"op": "replace", "path": "/email", "value": "john@example.com"}],
    )
    assert response.status == 400
    assert response.reason == "Only password can be patched."


async def test_patch_too_many_fields(client):
    """We currently only support patching password, let be explicit when
    someone tries to patch something else.
    """
    await client.app["identity_backend"].register_user(
        "test", "test", "foo@example.com"
    )
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        json=[
            {"op": "replace", "path": "/password", "value": "passwod"},
            {"op": "replace", "path": "/email", "value": "john@example.com"},
        ],
    )
    assert response.status == 400
    assert response.reason == "Only password can be patched."


async def test_patch_unexisting_user_with_existing_jwt(client, valid_jwt):
    """Even with a valid JWT, if the user just does not exist, we can't
    use the JWT.
    """
    response = await client.patch(
        "/users/toto/",
        headers={"Authorization": "Bearer " + valid_jwt},
        json=[{"op": "replace", "path": "/password", "value": "passwod"}],
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
        json=[{"op": "replace", "path": "/password", "value": "passwod"}],
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
        json=[{"op": "replace", "path": "/password", "value": "passwod"}],
    )
    assert response.status == 403
    assert "Token does not apply" in response.reason


async def test_patch_users_missing_auth(client):
    response = await client.patch(
        "/users/test/",
        json=[{"op": "replace", "path": "/password", "value": "passwod"}],
    )
    assert response.status == 401


async def test_patch_users_bad_auth(client):
    response = await client.patch(
        "/users/test/",
        headers={"Authorization": "I AM ROOT TAHHTS IT"},
        json=[{"op": "replace", "path": "/password", "value": "passwod"}],
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
