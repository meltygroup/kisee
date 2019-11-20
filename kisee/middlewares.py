"""Middlewares for Kisee service
"""

import json
from typing import Callable, Awaitable

from aiohttp import web

from kisee.serializers import serialize


Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


@web.middleware
async def verify_input_body_is_json(
    request: web.Request, handler: Handler
) -> web.StreamResponse:
    """
    Middleware to convert JSONDecodeError to HTTPBadRequest.
    """
    try:
        return await handler(request)
    except json.decoder.JSONDecodeError as err:
        raise web.HTTPBadRequest(reason="Malformed JSON.") from err


@web.middleware
async def coreapi_error_middleware(
    request: web.Request, handler: Handler
) -> web.StreamResponse:
    """Implementation of:
    http://www.coreapi.org/specification/transport/#coercing-4xx-and-5xx-responses-to-errors
    """
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return serialize(
            request, {"_type": "error", "_meta": {"title": ex.reason}}, ex.status
        )
