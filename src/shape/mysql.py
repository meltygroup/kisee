"""Binding between the identification server and our database with our
own specific model and PHP's blowfish.
"""


from typing import Union

import hmac
import aiomysql
import bcrypt

from aiohttp import web

from shapeidp.identity_provider import IdentityProvider


def constant_time_compare(val1: str, val2: str) -> bool:
    """Return True if the two strings are equal, False otherwise."""
    return hmac.compare_digest(val1, val2)


def verify(password: str, encoded: str) -> bool:
    """Verity that the given encoded (hashed) password is matching the
    expected password.

    Needs the bcrypt library.  Please be warned that this library
    depends on native C code and might cause portability issues.

    This is compatible with PHP's CRYPT_BLOWFISH (prefix is '$2y$').
    """
    if not encoded.startswith("$2y$"):
        raise RuntimeError(
            "The encoded string must be PHP's CRYPT_BLOWFISH compatible."
        )
    encoded_2 = bcrypt.hashpw(password, encoded)
    return constant_time_compare(encoded, encoded_2)


class DataStore(IdentityProvider):
    """Exposing shape internals as the requiered API for the
    identification server.
    """

    def __init__(self, options: dict) -> None:
        IdentityProvider.__init__(self, options)
        self.pool = None

    async def on_startup(self, app: web.Application):
        """Called by aiohttp on startup.
        """
        del app  # unused
        self.pool = await aiomysql.create_pool(
            host=self.options["host"],
            port=self.options["port"],
            user=self.options["user"],
            password=self.options["password"],
            db=self.options["database"],
        )

    async def on_cleanup(self, app: web.Application):
        """Called by aiohttp.
        """
        del app  # unused
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()

    async def identify(self, login: str, password: str) -> Union[dict, None]:
        """Identifies the given login/password pair, returns a dict if found.
        """
        if self.pool is not None:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(
                        "SELECT * FROM system2_info where login = %s", (login,)
                    )
                    user = await cur.fetchone()
            if verify(password.encode("utf8"), user["password"].encode("utf8")):
                return user
        return None
