"""This is a really dumb identification backend: it does not store
anything and accepts ANY login/password pair.
"""


from typing import Union
from aiohttp import web
from kisee.identity_provider import IdentityProvider


class DumbIdentityBackend(IdentityProvider):
    """Dumb dumb identity backend replying yes everytime.
    """

    async def on_startup(self, app: web.Application):
        pass

    async def on_cleanup(self, app: web.Application):
        pass

    async def identify(self, login: str, password: str) -> Union[dict, None]:
        # pylint: disable=unused-argument
        return {"login": login}
