"""Postgresql backend for Kisee
"""
import uuid
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
    """Postgresql backend for kisee"""

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

    async def identify(self, username: str, password: str) -> Optional[User]:
        """Identifies the given username/password pair, returns a dict if found."""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "SELECT * FROM users WHERE (username = $1 OR email = $1) ", username
            )
            if verify(password.encode("utf-8"), result["password"].encode("utf-8")):
                return User(
                    result["user_id"], result["username"], result["is_superuser"]
                )
        return None

    async def register_user(
        self, username: str, password: str, email: str, is_superuser: bool = False
    ):
        password_hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user_id = str(uuid.uuid4())
        async with self.pool.acquire() as connection:
            try:
                await connection.execute(
                    """
                    INSERT INTO users(
                        user_id, username, password, email, is_superuser
                    ) VALUES (
                        $1, $2, $3, $4, $5
                    )
                """,
                    user_id,
                    username,
                    password_hashed.decode("utf-8"),
                    email,
                    is_superuser,
                )
            except asyncpg.exceptions.UniqueViolationError:
                raise UserAlreadyExist

    async def get_user_by_email(self, email):
        """Get user with provided email address"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                """SELECT * FROM users WHERE email = $1""", email
            )
        user_data = dict(result)
        del user_data["password"]
        return User(**user_data)

    async def get_user_by_username(self, username):
        """Get user with provided username"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                """"SELECT * FROM users WHERE username = $1""", username
            )
        user_data = dict(result)
        del user_data["password"]
        return User(**user_data)

    async def set_password_for_user(self, user: User, password: str):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                    UPDATE users
                    SET password = $1
                    WHERE username = $2
                """,
                password,
                user.username,
            )

    async def is_connection_alive(self) -> bool:
        """Verify that connection is alive, always return True"""
        try:
            async with self.pool.acquire() as connection:
                connection.execute("SELECT 1")
                return True
        except AttributeError:
            return False
