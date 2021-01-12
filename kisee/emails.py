"""Email utils
"""


def is_email(email: str) -> bool:
    """Assert that email has minimun requirements, can be splited in two parts with '@'"""
    return "@" in email
