"""Email utils
"""

import re


def is_email(email: str) -> bool:
    """Assert that email has minimun requirements."""
    return re.search(r".+@.+\..+$", email) is not None
