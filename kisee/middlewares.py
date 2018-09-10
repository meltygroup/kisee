"""Middlewares for Kisee service
"""

import json
from typing import Callable

from aiohttp import web


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
