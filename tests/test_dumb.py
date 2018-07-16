"""Tests for the dumb identity provider
"""


from providers.dumb import DumbIdentityBackend


async def test_dumb_idp():
    """Test instanciation and identification
    """
    idp = DumbIdentityBackend({})
    identity = await idp.identify("dummy_login", "dummy_password")
    assert identity["login"] == "dummy_login"
