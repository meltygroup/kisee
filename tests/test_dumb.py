"""Tests for the dumb identity provider
"""


from kisee.providers.test import TestBackend


async def test_dumb_idp():
    """Test instanciation and identification
    """
    async with TestBackend({}) as test_backend:
        identity = await test_backend.identify("dummy_login", None, "")
        assert identity is None
        identity = await test_backend.identify("dummy_login", None, "dummy_password")
        assert identity.login == "dummy_login"
