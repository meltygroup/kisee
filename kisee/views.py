"""Views for the IdP server, implementing:

- GET /
- GET /jwt/
- POST /jwt/
"""

import json
from datetime import datetime, timedelta

import logging
import coreapi
import jwt
import shortuuid
from aiohttp import web
import psutil

from kisee.serializers import serialize


logger = logging.getLogger(__name__)


async def get_root(request: web.Request) -> web.Response:
    """https://tools.ietf.org/html/draft-nottingham-json-home-06
    """
    del request  # unused
    return web.Response(
        body=json.dumps(
            {
                "api": {
                    "title": "Identification Provider",
                    "links": {
                        "author": "mailto:julien@palard.fr",
                        "describedBy": "https://doc.meltylab.fr",
                    },
                },
                "resources": {
                    "jwt": {
                        "href": "/jwt/",
                        "hints": {
                            "allow": ["GET", "POST"],
                            "formats": {"application/coreapi+json": {}},
                        },
                    }
                },
            }
        ),
        content_type="application/json-home",
    )


async def get_jwts(request: web.Request) -> web.Response:
    """Handlers for GET /jwt/, just describes that a POST is possible.
    """
    return serialize(
        request,
        coreapi.Document(
            url="/jwt/",
            title="JSON Web Tokens",
            content={
                "tokens": [],
                "add_token": coreapi.Link(
                    action="post",
                    title="Create a new JWT",
                    description="POSTing to this endpoint create JWT tokens.",
                    fields=[
                        coreapi.Field(name="login", required=True),
                        coreapi.Field(name="password", required=True),
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
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        raise web.HTTPUnprocessableEntity(reason="Malformed JSON.")
    if "login" not in data or "password" not in data:
        raise web.HTTPUnprocessableEntity(reason="Missing login or password.")
    logger.debug("Trying to identify user %s", data["login"])
    user = await request.app.identity_backend.identify(data["login"], data["password"])
    if user is None:
        raise web.HTTPForbidden(reason="Failed identification.")
    jti = shortuuid.uuid()
    return serialize(
        request,
        coreapi.Document(
            url="/jwt/",
            title="JSON Web Tokens",
            content={
                "tokens": [
                    jwt.encode(
                        {
                            "iss": request.app.settings["jwt"]["iss"],
                            "sub": user.login,
                            "exp": datetime.utcnow() + timedelta(hours=1),
                            "jti": jti,
                        },
                        request.app.settings["jwt"]["private_key"],
                        algorithm="ES256",
                    ).decode("utf8")
                ],
                "add_token": coreapi.Link(
                    action="post",
                    title="Create a new JWT",
                    description="POSTing to this endpoint create JWT tokens.",
                    fields=[
                        coreapi.Field(name="login", required=True),
                        coreapi.Field(name="password", required=True),
                    ],
                ),
            },
        ),
        status=201,
        headers={"Location": "/jwt/" + jti},
    )


async def get_health(request: web.Request) -> web.Response:
    """Get service health metrics
    """
    is_database_ok = (
        "OK" if await request.app.identity_backend.is_connection_alive() else "KO"
    )
    disk_usage = psutil.disk_usage("/")
    disk_free_percentage = disk_usage.free / disk_usage.total * 100
    return web.Response(
        body=json.dumps(
            {
                "overall": "OK",
                "load_average": open("/proc/loadavg").readline().split(" ")[0],
                "database": is_database_ok,
                "disk_free": f"{disk_free_percentage:.2f}%",
            }
        ),
        content_type="application/json",
    )
