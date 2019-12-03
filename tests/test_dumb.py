"""Tests for the dumb identity provider
"""


from kisee.providers.demo import DemoBackend


async def test_dumb_idp():
    """Test instanciation and identification
    """
    async with DemoBackend() as test_backend:
        identity = await test_backend.identify("dummy_login", "")
        assert identity is None
        identity = await test_backend.identify("dummy_login", "dummy_password")
        assert identity is None
        await test_backend.register_user(
            "dummy_login", "dummy_password", "dummy@example.com"
        )
        identity = await test_backend.identify("dummy_login", "dummy_password")
        assert identity.username == "dummy_login"
