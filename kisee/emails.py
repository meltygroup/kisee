"""Email utils
"""

import re


def is_email(email: str) -> bool:
    """Assert that email has minimun requirements."""
    return re.search(".+@.+\..+$", email) is not None
