"""This is a really dumb identification backend: it does not store
anything and accepts ANY login/password pair.
"""


from aiohttp import web


class DumbIdentityBackend:
    """Dumb dumb identity backend replying yes everytime.
    """

    def __init__(self, options: dict) -> None:
        self.options = options

    async def on_startup(self, app: web.Application):
        """Called by aiohttp on startup.
        """
        pass

    async def on_cleanup(self, app: web.Application):
        """Called by aiohttp.
        """
        pass

    async def identify(self, login: str, password: str) -> dict:
        """Identifies the given login/password pair, returns a dict if found.
        """
        # pylint: disable=unused-argument
        return {"login": login}
