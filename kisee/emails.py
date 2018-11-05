"""Email utils
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple


def is_email(email: str) -> bool:
    """Assert that email has minimun requirements, can be splited in two parts with '@'
    """
    return "@" in email


def send_mail(subject: str, text: str, html: str, email_settings: dict, recipient: str):
    """Basically send a multipart/alternative email with text and HTML to
    recipient
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_settings["sender"]
    msg.add_header("reply-to", email_settings["sender"])
    msg["To"] = recipient
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP(email_settings.get("host", "localhost")) as smtp_server:
        smtp_server.sendmail(email_settings["sender"], recipient, msg.as_string())


def forge_forgotten_email(username: str, email: str, token: str) -> Tuple[str, str]:
    """Return email template
    """
    del email
    del token
    return (
        f"""
        Salut {username},

        Un mot de passe est si vite oublié !
        Une demande de récuperation de mot de passe à été enregistrée.
    """,
        f"""
    <p>Salut {username},</p>
    <p>
        Un mot de passe est si vite oublié !
        Une demande de récuperation de mot de passe à été enregistrée.
    </p>
    """,
    )
