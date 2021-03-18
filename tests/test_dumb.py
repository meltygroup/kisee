"""Tests for the dumb identity provider
"""


async def test_dumb_idp(backend):
    """Test instanciation and identification
    """
    identity = await backend.identify("dummy_login", "")
    assert identity is None
    identity = await backend.identify("dummy_login", "dummy_password")
    assert identity is None
    await backend.register_user("dummy_login", "dummy_password", "dummy@example.com")
    identity = await backend.identify("dummy_login", "dummy_password")
    assert identity.username == "dummy_login"
