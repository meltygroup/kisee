import smtplib
from kisee.emails import send_mail


class MockSMTP:
    sent_emails = []

    def __init__(self, *args, **kwargs):
        super().__init__()

    def __enter__(self):
        MockSMTP.sent_emails = []
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ...

    def sendmail(self, *args, **kwargs):
        self.sent_emails.append((args, kwargs))


def test_send_mail(monkeypatch):
    monkeypatch.setattr(smtplib, "SMTP", MockSMTP)
    send_mail(
        "Subject",
        "texttexttext",
        "htmlhtmlhtml",
        {"sender": "bar@localhost"},
        "foo@localhost",
    )
    assert len(MockSMTP.sent_emails) == 1
    assert MockSMTP.sent_emails[0][0][1] == "foo@localhost"
