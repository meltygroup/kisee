"""Authentication handler
"""
import base64
import binascii
from typing import Mapping, Tuple, Union

import jwt
from aiohttp import web

from kisee.identity_provider import IdentityProvider, User

Claims = Mapping[str, Union[str, bool, int]]


async def _basic_authentication(
    encoded: str, idp: IdentityProvider
) -> Tuple[User, Claims]:
    """Authentication using Basic scheme."""
    try:
        decoded = base64.b64decode(encoded)
    except binascii.Error as err:
        raise web.HTTPUnauthorized(reason="Bad authorization") from err
    try:
        username, password = decoded.decode("utf-8").split(":", 1)
    except ValueError as err:
        raise web.HTTPUnauthorized(reason="Bad authorization") from err
    user = await idp.identify(username, password)
    if user is None:
        raise web.HTTPUnauthorized(reason="Bad authorization")
    # Using basic auth means user knows its password so he's authorized to change it.
    return user, {}


async def _jwt_authentication(
    token: str,
    idp: IdentityProvider,
    public_key: str,
    for_password_modification=False,
) -> Tuple[User, Claims]:
    """Authentication using JWT."""
    try:
        claims = jwt.decode(token, public_key, algorithms=["ES256"])
    except jwt.DecodeError as err:
        raise web.HTTPUnauthorized(reason="Bad authorization") from err
    else:
        if for_password_modification:
            if "password_reset_for" not in claims:
                raise web.HTTPForbidden(
                    reason="Use a password lost token or basic auth."
                )
            user = await idp.get_user_by_username(claims["password_reset_for"])
        else:
            user = await idp.get_user_by_username(claims["sub"])
        if not user:
            raise web.HTTPUnauthorized(reason="No such user")
        return user, claims


async def authenticate_user(
    request: web.Request, for_password_modification=False
) -> Tuple[User, Claims]:
    """Multiple schemes authentication using request Authorization header.
    Raises HTTPUnauthorized on failure.
    """
    if not request.headers.get("Authorization"):
        raise web.HTTPUnauthorized(reason="Missing authorization header")
    scheme, value = request.headers["Authorization"].strip().split(" ", 1)
    if scheme == "Basic":
        return await _basic_authentication(value, request.app["identity_backend"])
    if scheme == "Bearer":
        return await _jwt_authentication(
            value,
            request.app["identity_backend"],
            request.app["settings"]["jwt"]["public_key"],
            for_password_modification=for_password_modification,
        )
    raise web.HTTPUnauthorized(reason="Bad authorization")
