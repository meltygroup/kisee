"""Authentication handler
"""
import base64
from typing import Optional

from aiohttp import web

from kisee.identity_provider import IdentityProvider, User


async def basic_authentication(encoded: bytes, idp: IdentityProvider) -> Optional[User]:
    """Authentication using Basic scheme
    """
    decoded = base64.b64decode(encoded)
    username, password = decoded.decode("utf-8").split(":", 1)
    return await idp.identify(username, password)


async def reset_token_authentication(
    token: str, idp: IdentityProvider
) -> Optional[User]:
    """Verify that token belongs to a user
    """
    return await idp.retrieve_user_from_rst_token(token)


async def authenticate_user(request: web.Request) -> User:
    """Multiple schemes authentication using request Authorization header
    """
    if not request.headers.get("Authorization"):
        raise web.HTTPUnauthorized(reason="Missing authorization header")
    scheme, value = request.headers.get("Authorization").strip().split(" ")
    user = None
    if scheme == "Basic":
        user = await basic_authentication(value, request.app.identity_backend)
    elif scheme == "rst_token":
        user = await reset_token_authentication(value, request.app.identity_backend)
    if not user:
        raise web.HTTPUnauthorized(reason="No authentication provided")
    return user
