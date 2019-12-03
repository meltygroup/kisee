"""Mocks for kisee service
"""


def send_mail(subject, text, html, email_settings, recipient):
    """Do not send a mail during the tests.
    """
