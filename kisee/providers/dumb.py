"""This is a really dumb identification backend: it does not store
anything and accepts ANY login/password pair.
"""


from typing import Optional

from kisee.identity_provider import IdentityProvider, User


class DumbIdentityBackend(IdentityProvider):
    """Dumb dumb identity backend replying yes everytime.
    """

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def identify(self, login: str, password: str) -> Optional[User]:
        # pylint: disable=unused-argument
        return User(login)
