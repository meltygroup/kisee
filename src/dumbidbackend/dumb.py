"""This is a really dumb identification backend: it does not store
anything and accepts ANY login/password pair.
"""


from shapeidp.identity_provider import IdentityProvider


class DumbIdentityBackend(IdentityProvider):
    """Dumb dumb identity backend replying yes everytime.
    """

    def __init__(self, options: dict) -> None:
        IdentityProvider.__init__(self, options)

    async def identify(self, login: str, password: str) -> dict:
        """Identifies the given login/password pair, returns a dict if found.
        """
        # pylint: disable=unused-argument
        return {"login": login}
