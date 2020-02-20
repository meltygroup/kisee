"""Views for the IdP server, implementing:

- GET /
- GET /jwt/
- POST /jwt/
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

import jwt
import shortuuid
from aiohttp import web
from aiojobs.aiohttp import spawn

import kisee
from kisee.authentication import authenticate_user
from kisee.emails import is_email
from kisee.identity_provider import UserAlreadyExist, ProviderError
from kisee.serializers import serialize
from kisee import serializers
from kisee.utils import get_user_with_email_or_username

logger = logging.getLogger(__name__)


async def get_root(
    request: web.Request,  # pylint: disable=unused-argument
) -> web.Response:
    """https://tools.ietf.org/html/draft-nottingham-json-home-06
    """
    hostname = request.app["settings"]["server"]["hostname"]
    home = {
        "api": {
            "title": "Identification Provider",
            "links": {
                "author": "mailto:julien@palard.fr",
                "describedBy": "https://kisee.readthedocs.io",
            },
        },
        "resources": {
            "jwt": {
                "href": f"{hostname}/jwt/",
                "hints": {
                    "allow": ["GET", "POST"],
                    "formats": {"application/coreapi+json": {}},
                },
            },
            "users": {
                "href": f"{hostname}/users/",
                "hints": {
                    "allow": ["GET", "POST", "PATCH"],
                    "formats": {"application/coreapi+json": {}},
                },
            },
            "forgotten_passwords": {
                "href": f"{hostname}/forgotten_passwords/",
                "hints": {
                    "allow": ["GET", "POST"],
                    "formats": {"application/coreapi+json": {}},
                },
            },
        },
        "actions": {
            "register_user": {
                "href": f"{hostname}/users/",
                "method": "POST",
                "fields": [
                    {"name": "username", "required": True},
                    {"name": "password", "required": True},
                    {"name": "email", "required": True},
                ],
            },
            "create_token": {
                "href": f"{hostname}/jwt/",
                "method": "POST",
                "fields": [
                    {"name": "username", "required": True},
                    {"name": "password", "required": True},
                ],
            },
        },
    }
    return web.Response(
        body=json.dumps(home, indent=4), content_type="application/json-home"
    )


async def get_users(request: web.Request) -> web.Response:
    """View for GET /users/, just describes that a POST is possible.
    """
    return serialize(
        request,
        serializers.Document(
            url="/users/",
            title="Users",
            content={
                "users": [],
                "register_user": serializers.Link(
                    url="/users/",
                    action="post",
                    title="Register a new user",
                    description="POSTing to this endpoint creates a new user",
                    fields=[
                        serializers.Field(
                            name="username",
                            required=True,
                            schema={"type": "string", "minLength": 3},
                        ),
                        serializers.Field(
                            name="password",
                            required=True,
                            schema={
                                "type": "string",
                                "minLength": 5,
                                "format": "password",
                            },
                        ),
                        serializers.Field(
                            name="email",
                            required=True,
                            schema={"type": "string", "format": "email"},
                        ),
                    ],
                ),
            },
        ),
    )


async def post_users(request: web.Request) -> web.Response:
    """A client is asking to create a new user.
    """
    data = await request.json()

    if not all(key in data.keys() for key in {"username", "email", "password"}):
        raise web.HTTPBadRequest(reason="Missing required input fields")

    logger.debug("Trying to create user %s", data["username"])

    if not is_email(data["email"]):
        raise web.HTTPBadRequest(reason="Email is not valid")

    try:
        await request.app["identity_backend"].register_user(
            data["username"], data["password"], data["email"]
        )
    except UserAlreadyExist:
        raise web.HTTPConflict(reason="User already exist")
    except ProviderError as err:
        raise web.HTTPBadRequest(reason=str(err))

    location = f"/users/{data['username']}/"
    return web.Response(status=201, headers={"Location": location})


async def patch_user(request: web.Request) -> web.Response:
    """Patch user password
    """
    user, _ = await authenticate_user(request, for_password_modification=True)
    data = await request.json()
    if "password" not in data:
        raise web.HTTPBadRequest(reason="Missing fields to patch")
    username = request.match_info["username"]
    if username != user.username:
        raise web.HTTPForbidden(reason="Token does not apply to user resource")
    await request.app["identity_backend"].set_password_for_user(user, data["password"])
    return web.Response(status=204)


async def get_jwts(request: web.Request) -> web.Response:
    """Handlers for GET /jwt/, just describes that a POST is possible.
    """
    return serialize(
        request,
        serializers.Document(
            url=f"/jwt/",
            title="JSON Web Tokens",
            content={
                "tokens": [],
                "add_token": serializers.Link(
                    url="/jwt/",
                    action="post",
                    title="Create a new JWT",
                    description="POSTing to this endpoint create JWT tokens.",
                    fields=[
                        serializers.Field(
                            name="username", required=True, schema={"type": "string"}
                        ),
                        serializers.Field(
                            name="password",
                            required=True,
                            schema={"type": "string", "format": "password"},
                        ),
                    ],
                ),
            },
        ),
    )


async def get_jwt(request: web.Request) -> web.Response:
    """Handler for GET /jwt{/jid}.
    """
    del request  # unused
    raise NotImplementedError()


async def post_jwt(request: web.Request) -> web.Response:
    """A user is asking for a JWT.
    """
    data = await request.json()
    if ("login" not in data and "username" not in data) or "password" not in data:
        raise web.HTTPUnprocessableEntity(reason="Missing username or password.")
    username = data.get("username", data.get("login", ""))
    logger.debug("Trying to identify user %s", username)
    user = await request.app["identity_backend"].identify(username, data["password"])
    if user is None:
        raise web.HTTPForbidden(reason="Failed identification for kisee.")
    jti = shortuuid.uuid()
    return serialize(
        request,
        serializers.Document(
            url="/jwt/",
            title="JSON Web Tokens",
            content={
                "tokens": [
                    jwt.encode(
                        {
                            "iss": request.app["settings"]["jwt"]["iss"],
                            "sub": user.user_id,
                            "exp": datetime.utcnow() + timedelta(hours=1),
                            "jti": jti,
                        },
                        request.app["settings"]["jwt"]["private_key"],
                        algorithm="ES256",
                    ).decode("utf8")
                ],
                "add_token": serializers.Link(
                    url="/jwt/",
                    action="post",
                    title="Create a new JWT",
                    description="POSTing to this endpoint create JWT tokens.",
                    fields=[
                        serializers.Field(
                            name="username", required=True, schema={"type": "string"}
                        ),
                        serializers.Field(
                            name="password",
                            required=True,
                            schema={"type": "string", "format": "password"},
                        ),
                    ],
                ),
            },
        ),
        status=201,
        headers={"Location": "/jwt/" + jti},
    )


async def get_forgotten_passwords(request: web.Request) -> web.Response:
    """Get forgotten password view, just describes that a POST is possible.
    """
    return serialize(
        request,
        serializers.Document(
            url=f"/forgotten_passwords/",
            title="Forgotten password management",
            content={
                "reset_password": serializers.Link(
                    url="/forgotten-password/",
                    action="post",
                    title="",
                    description="POSTing to this endpoint subscribe "
                    "for a forgotten password",
                    fields=[
                        serializers.Field(name="username", schema={"type": "string"}),
                        serializers.Field(
                            name="email", schema={"type": "string", "format": "email"}
                        ),
                    ],
                )
            },
        ),
    )


async def _post_forgotten_passwords(request: web.Request) -> None:
    """Locate a user and send him a password reset token.
    """
    data = await request.json()
    user = await get_user_with_email_or_username(data, request.app["identity_backend"])
    if not user:
        return
    jwt_token = jwt.encode(
        {
            "iss": request.app["settings"]["jwt"]["iss"],
            "exp": datetime.utcnow() + timedelta(hours=12),
            "jti": shortuuid.uuid(),
            "password_reset_for": user.username,
        },
        request.app["settings"]["jwt"]["private_key"],
        algorithm="ES256",
    ).decode("utf-8")
    await request.app["identity_backend"].send_reset_password_challenge(user, jwt_token)


async def post_forgotten_passwords(request: web.Request) -> web.Response:
    """Start the password recovery process.

    This works mostly on background, so no timing attack can be used
    to probe for emails.
    """
    data = await request.json()
    if "username" not in data and "email" not in data and "login" not in data:
        raise web.HTTPBadRequest(reason="Missing required fields email or username")
    await spawn(request, _post_forgotten_passwords(request))
    return web.Response(status=201)


async def get_health(request: web.Request) -> web.Response:
    """Get service health metrics
    """
    status = "green"
    error = None
    is_database_ok = await request.app["identity_backend"].is_connection_alive()
    if not is_database_ok:
        status = "red"
        error = {"str": "Database looks down."}
    health: Dict[str, Any] = {
        "status": status,
        "database": "OK" if is_database_ok else "KO",
        "version": kisee.__version__,
    }
    if error:
        health["error"] = error
    return web.Response(
        body=json.dumps(health, indent=4), content_type="application/json"
    )
