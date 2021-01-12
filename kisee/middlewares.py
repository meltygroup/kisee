"""Middlewares for Kisee service
"""

import json
from typing import Callable, Awaitable

from aiohttp import web


Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

@web.middleware
async def vary_origin(request: web.Request, handler: Handler) -> web.Response:
    """Add a Vary: Origin to the responses.

    See: https://github.com/aio-libs/aiohttp-cors/issues/351
    """
    response = await handler(request)
    response.headers["Vary"] = "Origin"
    return response

@web.middleware
async def enforce_json(request: web.Request, handler: Handler) -> web.Response:
    """Middleware enforcing a JSON response.
    """
    try:
        return await handler(request)
    except json.JSONDecodeError as err:
        document = {
            "_type": "error",
            "_meta": {"title": "Malformed JSON"},
            "title": "Malformed JSON",
            "detail": str(err),
            "status": 400,
        }
    except web.HTTPException as err:
        document = {
            "_type": "error",
            "_meta": {"title": err.reason},
            "title": err.reason,
            "status": err.status,
        }
    return web.Response(
        text=json.dumps(document, indent=4),
        status=document["status"],  # type: ignore
        reason=document["title"],  # type: ignore
        content_type="application/problem+json",
    )
