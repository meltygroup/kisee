"""Some utils for kisee
"""
from kisee.identity_provider import IdentityProvider, User, Optional


async def get_user_with_email_or_username(
    user_input: dict, idp_backend: IdentityProvider
) -> Optional[User]:
    """Retrieve user with either email or username
    """
    if "email" in user_input:
        return await idp_backend.get_user_by_email(user_input["email"])
    if "login" in user_input:  # For backward compatibility
        return await idp_backend.get_user_by_username(user_input["login"])
    return await idp_backend.get_user_by_username(user_input["username"])
