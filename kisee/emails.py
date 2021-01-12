"""Email utils
"""


def is_email(email: str) -> bool:
    """Assert that email has minimun requirements."""
    return "@" in email
