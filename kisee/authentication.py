"""Authentication handler
"""
import base64
from typing import Optional

import jwt
from aiohttp import web

from kisee.identity_provider import IdentityProvider, User


async def basic_authentication(encoded: bytes, idp: IdentityProvider) -> Optional[User]:
    """Authentication using Basic scheme
    """
    decoded = base64.b64decode(encoded)
    username, password = decoded.decode("utf-8").split(":", 1)
    return await idp.identify(username, password)


async def jwt_authentication(
    token: str, idp: IdentityProvider, public_key: str
) -> Optional[User]:
    """Verify that token belongs to a user
    """
    claims = jwt.decode(token, public_key, algorithms="ES256")
    if claims.get("forgotten_password"):
        return await idp.get_user_by_username(claims["sub"])
    return None


async def authenticate_user(request: web.Request) -> User:
    """Multiple schemes authentication using request Authorization header
    """
    if not request.headers.get("Authorization"):
        raise web.HTTPUnauthorized(reason="Missing authorization header")
    scheme, value = request.headers.get("Authorization").strip().split(" ")
    user = None
    if scheme == "Basic":
        user = await basic_authentication(value, request.app.identity_backend)
    elif scheme == "Bearer":
        user = await jwt_authentication(
            value,
            request.app.identity_backend,
            request.app.settings["jwt"]["public_key"],
        )
    if not user:
        raise web.HTTPUnauthorized(reason="No authentication provided")
    return user

