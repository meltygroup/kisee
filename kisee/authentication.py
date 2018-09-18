"""Authentication handler
"""
import base64

from aiohttp import web

from kisee.identity_provider import IdentityProvider, User


def basic_authentication(encoded: str, idp: IdentityProvider) -> User or None:
    """Authentication using Basic scheme
    """
    decoded = base64.b64decode(encoded)
    username, password = decoded.split(":", 1)
    return idp.identify(username, password)


def authenticate_user(request: web.Request) -> User:
    """Multiple schemes authentication using request Authorization header
    """
    if not request.headers.get("Authorization"):
        raise web.HTTPUnauthorized(reason="Missing authorization header")
    scheme, value = request.headers.get("Authorization").strip().split(" ")
    if scheme == "Basic":
        return basic_authentication(value, request.app.identity_backend)
    raise web.HTTPUnauthorized(reason="No authentication provided")
