"""Middlewares for Kisee service
"""

import json
from typing import Callable

from aiohttp import web

from kisee.serializers import serialize


@web.middleware
async def verify_input_body_is_json(
    request: web.Request, handler: Callable
) -> Callable:
    """
    Middleware to verify that input body is of json format
    """
    if request.can_read_body:
        try:
            await request.json()
        except json.decoder.JSONDecodeError:
            raise web.HTTPBadRequest(reason="Malformed JSON.")
    return await handler(request)


@web.middleware
async def coreapi_error_middleware(request, handler):
    """Implementation of:
    http://www.coreapi.org/specification/transport/#coercing-4xx-and-5xx-responses-to-errors
    """
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return serialize(
            request, {"_type": "error", "_meta": {"title": ex.reason}}, ex.status
        )
