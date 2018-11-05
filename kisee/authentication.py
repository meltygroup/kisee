"""Authentication handler
"""
import base64, binascii
from typing import Mapping, Tuple, Union

import jwt
from aiohttp import web

from kisee.identity_provider import IdentityProvider, User

Claims = Mapping[str, Union[str, bool, int]]


async def _basic_authentication(
    encoded: bytes, idp: IdentityProvider
) -> Tuple[User, Claims]:
    """Authentication using Basic scheme.
    """
    try:
        decoded = base64.b64decode(encoded)
    except binascii.Error:
        raise web.HTTPUnauthorized(reason="Bad authorization")
    try:
        username, password = decoded.decode("utf-8").split(":", 1)
    except ValueError:
        raise web.HTTPUnauthorized(reason="Bad authorization")
    user = await idp.identify(username, password)
    if user is None:
        raise web.HTTPUnauthorized(reason="Bad authorization")
    # Using basic auth means user knows its password so he's authorized to change it.
    return user, {"can_change_pwd": True}


async def _jwt_authentication(
    token: str, idp: IdentityProvider, public_key: str
) -> Tuple[User, Claims]:
    """Authentication using JWT.
    """
    try:
        claims = jwt.decode(token, public_key, algorithms="ES256")
    except jwt.DecodeError as err:
        raise web.HTTPUnauthorized(reason="Bad authorization") from err
    else:
        return await idp.get_user_by_username(claims["sub"]), claims


async def authenticate_user(request: web.Request) -> Tuple[User, Claims]:
    """Multiple schemes authentication using request Authorization header.
    Raises HTTPUnauthorized on failure.
    """
    if not request.headers.get("Authorization"):
        raise web.HTTPUnauthorized(reason="Missing authorization header")
    scheme, value = request.headers.get("Authorization").strip().split(" ", 1)
    if scheme == "Basic":
        return await _basic_authentication(value, request.app.identity_backend)
    if scheme == "Bearer":
        return await _jwt_authentication(
            value,
            request.app.identity_backend,
            request.app.settings["jwt"]["public_key"],
        )
    raise web.HTTPUnauthorized(reason="Bad authorization")
