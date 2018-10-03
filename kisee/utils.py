"""Utils for Kisee
"""


def is_email(email: str) -> bool:
    """Assert that email has minimum requirements
    """
    return "@" in email
