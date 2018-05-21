"""Binding between the identification server and our database with our
own specific model and PHP's blowfish.
"""

import hmac
import aiomysql
import bcrypt


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return hmac.compare_digest(val1, val2)


def verify(password, encoded):
    """Verity that the given encoded (hashed) password is matching the
    expected password.

    Needs the bcrypt library.  Please be warned that this library
    depends on native C code and might cause portability issues.

    This is compatible with PHP's CRYPT_BLOWFISH (prefix is '$2y$').
    """
    assert encoded.startswith(b'$2y$')
    encoded_2 = bcrypt.hashpw(password, encoded)
    return constant_time_compare(encoded, encoded_2)


class DataStore:
    """Exposing shape internals as the requiered API for the
    identification server.
    """
    def __init__(self, options):
        self.options = options
        self.pool = None

    async def on_startup(self, app):
        """Called by aiohttp on startup.
        """
        self.pool = await aiomysql.create_pool(
            host=self.options.get('host', '127.0.0.1'),
            port=self.options.get('port', 3306),
            user=self.options.get('user', 'root'),
            password=self.options.get('password', ''),
            db=self.options.get('database', 'test'))

    async def on_cleanup(self, app):
        """Called by aiohttp.
        """
        self.pool.close()
        await self.pool.wait_closed()

    async def identify(self, login, password):
        """Identifies the given login/password pair, returns a dict if found.
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT * FROM system2_info where login = %s",
                    (login, ))
                user = await cur.fetchone()
        if verify(password.encode('utf8'), user['password'].encode('utf8')):
            return user
        return None
