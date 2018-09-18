"""Utils for Kisee
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def is_email(email: str) -> bool:
    """Assert that email has minimum requirements
    """
    return "@" in email


def send_mail(subject, text, html, recipient):
    """Basically send a multipart/alternative email with text and HTML to
    recipient
    """
    pass


def forge_forgotten_email(username: str, email: str, token: str) -> str:
    return f"""
        Sends emails to {username} via {email} with token {token}
    """
