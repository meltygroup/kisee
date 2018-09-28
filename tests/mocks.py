"""Mocks for kisee service
"""
from kisee.identity_provider import UserAlreadyExist


def register_user(self, username, password, is_superuser=False):
    """Mocker register user
    """
    raise UserAlreadyExist


def send_mail(subject, text, html, email_settings, recipient):
    """Send mail
    """
    pass
