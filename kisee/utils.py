"""Some utils for kisee
"""
from kisee.identity_provider import IdentityProvider
from kisee.identity_provider import User


async def get_user_with_email_or_username(
    user_input: dict, idp_backend: IdentityProvider
) -> User:
    """Retrieve user with either email or username
    """
    if "email" in user_input:
        return await idp_backend.get_user_by_email(user_input["email"])
    return await idp_backend.get_user_by_username(user_input["login"])
