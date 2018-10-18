"""Postgresql backend for Kisee
"""


from typing import Optional

import hmac
import bcrypt
import asyncpg

from kisee.identity_provider import IdentityProvider, User, UserAlreadyExist


def constant_time_compare(val1: bytes, val2: bytes) -> bool:
    """Return True if the two strings are equal, False otherwise."""
    return hmac.compare_digest(val1, val2)


def verify(user_input: bytes, database_encoded: bytes) -> bool:
    """Verity that the given encoded (hashed) password is matching the
    expected password.

    Needs the bcrypt library.  Please be warned that this library
    depends on native C code and might cause portability issues.

    This is compatible with Python Blowfish cipher (prefix is '$2b$').
    """
    if not database_encoded.startswith(b"$2b$"):
        raise ValueError(
            "The encoded string must be Python Blowfish cipher compatible."
        )
    encoded_user_input = bcrypt.hashpw(user_input, database_encoded)
    return constant_time_compare(database_encoded, encoded_user_input)


class DataStore(IdentityProvider):
    """Postgresql backend for kisee
    """

    def __init__(self, options: dict, **kwargs) -> None:
        super().__init__(options, **kwargs)
        self.user = options["user"]
        self.password = options["password"]
        self.database = options["database"]
        self.host = options["host"]
        self.port = options["port"]

    async def __aenter__(self):
        self.pool = await asyncpg.create_pool(  # pylint: disable=W0201
            database=self.database,  # W0201 is attribute-defined-outside-init
            user=self.user,  # we define it outside of init on purpose
            password=self.password,
            host=self.host,
            port=self.port,
        )

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            self.pool.terminate()
        except AttributeError:
            pass

    async def identify(self, login: Optional[str], email: Optional[str], password: str) -> Optional[User]:
        """Identifies the given login/password pair, returns a dict if found.
        """
        async with self.pool.acquire() as connection:
            if login:
                result = await connection.fetchrow(
                    "SELECT * FROM users WHERE username = $1", login
                )
            else:
                result = await connection.fetchrow(
                    "SELECT * FROM users WHERE email = $1", email
                )
            if verify(password.encode("utf-8"), result["password"].encode("utf-8")):
                return User(result["username"], result["is_superuser"])
        return None

    async def register_user(
        self, username: str, password: str, is_superuser: bool = False
    ):
        async with self.pool.acquire() as connection:
            try:
                await connection.execute(
                    """
                    INSERT INTO users(
                        username, password, is_superuser
                    ) VALUES (
                        $1, $2, $3
                    )
                """,
                    username,
                    password,
                    is_superuser,
                )
            except asyncpg.exceptions.UniqueViolationError:
                raise UserAlreadyExist

    async def is_connection_alive(self) -> bool:
        """Verify that connection is alive, always return True
        """
        try:
            async with self.pool.acquire() as connection:
                connection.execute("SELECT 1")
                return True
        except AttributeError:
            return False
