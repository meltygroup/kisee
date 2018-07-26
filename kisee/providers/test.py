"""This is a really dumb identification backend: it does not store
anything and accepts almost any login/password pair.
"""


from typing import Optional

from kisee.identity_provider import IdentityProvider, User


class TestBackend(IdentityProvider):
    """Dumb identity backend, for test purposes.
    This backend follow the following rules:
     - Any user exist and have virtually all passwords.
     - Any password less or equal than 4 characters will fail.
     - root is a superuser.
    Yes, this mean than anybody logging as root with any password of
    more than 4 chars will be superuser. This is for test purposes only.
    """

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def identify(self, login: str, password: str) -> Optional[User]:
        """Identifies the given login/password pair, returns a dict if found.
        """
        # pylint: disable=unused-argument
        if len(password) < 4:
            return None
        return User(login=login, is_superuser=login == "root")
