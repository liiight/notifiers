"""
Offline tests for the email based providers (email, gmail, icloud).

``smtplib.SMTP`` / ``smtplib.SMTP_SSL`` are replaced by a fake that records every call and the sent message, so these
tests cover the full flow (arguments, defaults, validation, connection, TLS/SSL, login, the built message and the
response) without a network.
"""

from __future__ import annotations

import logging
import smtplib
import socket
from email.message import EmailMessage

import pytest

import notifiers
from notifiers.exceptions import BadArguments, NotificationError
from notifiers.logging import NotificationHandler
from notifiers.providers import email as email_provider

FQDN = "example.test"
DEFAULT_FROM = f"notifiers@{FQDN}"
DEFAULT_SUBJECT = "New email from 'notifiers'!"


class FakeSMTP:
    """Records the SMTP conversation. Class level state, reset per test by the ``smtp`` fixture"""

    instances: list[FakeSMTP] = []
    fail_with: Exception | None = None
    ssl = False

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.calls: list[tuple] = []
        self.sent: list[EmailMessage] = []
        type(self).instances.append(self)
        if type(self).fail_with:
            raise type(self).fail_with

    def ehlo(self):
        self.calls.append(("ehlo",))

    def starttls(self):
        self.calls.append(("starttls",))

    def login(self, username, password):
        self.calls.append(("login", username, password))

    def send_message(self, message):
        self.sent.append(message)


class FakeSMTPSSL(FakeSMTP):
    ssl = True


@pytest.fixture
def smtp(monkeypatch):
    FakeSMTP.instances = []
    FakeSMTP.fail_with = None
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTPSSL)
    monkeypatch.setattr(socket, "getfqdn", lambda *_: FQDN)
    email_provider.default_from.cache_clear()
    for key in list(__import__("os").environ):
        if key.startswith(("NOTIFIERS_EMAIL_", "NOTIFIERS_GMAIL_", "NOTIFIERS_ICLOUD_")):
            monkeypatch.delenv(key)
    yield FakeSMTP
    email_provider.default_from.cache_clear()


def sent_message(smtp) -> EmailMessage:
    (connection,) = smtp.instances
    (message,) = connection.sent
    return message


def body(message: EmailMessage) -> tuple[str, str]:
    part = next(p for p in message.walk() if not p.is_multipart() and p.get_content_disposition() != "attachment")
    return part.get_content_type(), part.get_content().strip()


class TestEmail:
    provider_name = "email"

    def notify(self, **kwargs):
        return notifiers.get_notifier(self.provider_name).notify(**kwargs)

    def test_minimal(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi")
        assert rsp.ok
        assert rsp.status == "Success"
        assert rsp.provider == "email"
        assert rsp.data == {
            "message": "hi",
            "to": "foo@foo.com",
            "subject": DEFAULT_SUBJECT,
            "from": DEFAULT_FROM,
            "host": "localhost",
            "port": 25,
            "tls": False,
            "ssl": False,
            "html": False,
            "login": True,
        }
        (connection,) = smtp.instances
        assert (type(connection), connection.host, connection.port) == (FakeSMTP, "localhost", 25)
        assert connection.calls == []
        message = sent_message(smtp)
        assert message["To"] == "foo@foo.com"
        assert message["From"] == DEFAULT_FROM
        assert message["Subject"] == DEFAULT_SUBJECT
        assert message["Date"]
        assert message["CC"] is None
        assert message["Bcc"] is None
        assert body(message) == ("text/plain", "hi")

    def test_module_level_notify(self, smtp):
        rsp = notifiers.notify("email", to="foo@foo.com", message="hi")
        assert rsp.ok
        assert sent_message(smtp)["To"] == "foo@foo.com"

    def test_multiple_to_is_comma_joined(self, smtp):
        rsp = self.notify(to=["foo@foo.com", "bar@foo.com"], message="hi")
        assert rsp.data["to"] == "foo@foo.com,bar@foo.com"
        assert sent_message(smtp)["To"] == "foo@foo.com, bar@foo.com"

    def test_tuple_to(self, smtp):
        rsp = self.notify(to=("foo@foo.com", "bar@foo.com"), message="hi")
        assert rsp.data["to"] == "foo@foo.com,bar@foo.com"

    @pytest.mark.parametrize(
        ("cc", "bcc"),
        [
            ("cc@foo.com", None),
            (None, "bcc@foo.com"),
            (["c1@foo.com", "c2@foo.com"], ["b1@foo.com", "b2@foo.com"]),
        ],
    )
    def test_cc_bcc(self, smtp, cc, bcc):
        kwargs = {k: v for k, v in {"cc": cc, "bcc": bcc}.items() if v is not None}
        rsp = self.notify(to="foo@foo.com", message="hi", **kwargs)
        assert rsp.ok
        message = sent_message(smtp)
        for header, value in (("CC", cc), ("Bcc", bcc)):
            if value is None:
                assert message[header] is None
                assert header.lower() not in rsp.data
            else:
                expected = value if isinstance(value, str) else ", ".join(value)
                assert message[header] == expected

    @pytest.mark.parametrize("key", ["from", "from_"])
    def test_from(self, smtp, key):
        rsp = self.notify(to="foo@foo.com", message="hi", **{key: "me@foo.com"})
        assert rsp.data["from"] == "me@foo.com"
        assert "from_" not in rsp.data
        assert sent_message(smtp)["From"] == "me@foo.com"

    def test_subject(self, smtp):
        self.notify(to="foo@foo.com", message="hi", subject="Hello")
        assert sent_message(smtp)["Subject"] == "Hello"

    def test_html(self, smtp):
        self.notify(to="foo@foo.com", message="<b>hi</b>", html=True)
        assert body(sent_message(smtp)) == ("text/html", "<b>hi</b>")

    def test_tls_and_login(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi", host="smtp.foo.com", port=587, tls=True, username="u", password="p")
        assert rsp.ok
        (connection,) = smtp.instances
        assert (type(connection), connection.host, connection.port) == (FakeSMTP, "smtp.foo.com", 587)
        assert connection.calls == [("ehlo",), ("starttls",), ("login", "u", "p")]

    def test_ssl(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi", host="smtp.foo.com", port=465, ssl=True, tls=True, username="u", password="p")
        assert rsp.ok
        (connection,) = smtp.instances
        assert type(connection) is FakeSMTPSSL
        # starttls is not used over an SSL connection
        assert connection.calls == [("login", "u", "p")]

    def test_ssl_without_tls(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi", port=465, ssl=True)
        assert rsp.ok
        (connection,) = smtp.instances
        assert type(connection) is FakeSMTPSSL
        assert ("starttls",) not in connection.calls

    def test_login_false_skips_login(self, smtp):
        self.notify(to="foo@foo.com", message="hi", username="u", password="p", login=False)
        (connection,) = smtp.instances
        assert ("login", "u", "p") not in connection.calls

    def test_attachments(self, smtp, tmp_path):
        files = {"a.txt": "text/plain", "b.pdf": "application/pdf", "c.jpg": "image/jpeg", "d.unknownext": "application/octet-stream"}
        paths = []
        for name in files:
            path = tmp_path / name
            path.write_text("content")
            paths.append(str(path))
        rsp = self.notify(to="foo@foo.com", message="hi", attachments=paths)
        assert rsp.data["attachments"] == paths
        attachments = list(sent_message(smtp).iter_attachments())
        assert [(a.get_filename(), a.get_content_type()) for a in attachments] == list(files.items())

    def test_single_attachment(self, smtp, tmp_path):
        path = tmp_path / "a.txt"
        path.write_text("content")
        rsp = self.notify(to="foo@foo.com", message="hi", attachments=str(path))
        assert rsp.ok
        assert rsp.data["attachments"] == [str(path)]
        assert [a.get_filename() for a in sent_message(smtp).iter_attachments()] == ["a.txt"]

    def test_connection_is_reused_for_same_configuration(self, smtp):
        provider = notifiers.get_notifier(self.provider_name)
        credentials = getattr(self, "credentials", {})
        provider.notify(to="foo@foo.com", message="one", **credentials)
        provider.notify(to="foo@foo.com", message="two", **credentials)
        (connection,) = smtp.instances
        assert len(connection.sent) == 2
        provider.notify(to="foo@foo.com", message="three", host="other.host", **credentials)
        assert len(smtp.instances) == 2

    def test_port_and_bool_strings_are_coerced(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi", port="2525", tls="true", username="u", password="p")
        assert rsp.data["port"] == 2525
        assert rsp.data["tls"] is True
        (connection,) = smtp.instances
        assert connection.port == 2525
        assert ("starttls",) in connection.calls

    @pytest.mark.parametrize(
        "error",
        [
            smtplib.SMTPServerDisconnected("Connection unexpectedly closed"),
            smtplib.SMTPAuthenticationError(535, b"Username and Password not accepted"),
            ConnectionRefusedError(61, "Connection refused"),
            socket.gaierror(8, "nodename nor servname provided"),
        ],
    )
    def test_smtp_errors_are_returned_in_response(self, smtp, error):
        smtp.fail_with = error
        rsp = self.notify(to="foo@foo.com", message="hi")
        assert not rsp.ok
        assert rsp.status == "Failure"
        assert rsp.errors == [str(error)]
        with pytest.raises(NotificationError):
            rsp.raise_on_errors()
        with pytest.raises(NotificationError):
            self.notify(to="foo@foo.com", message="hi", raise_on_errors=True)

    @pytest.mark.parametrize(
        ("data", "message"),
        [
            ({"message": "hi"}, "'to' is a required property"),
            ({"to": "foo@foo.com"}, "'message' is a required property"),
            ({"to": "not-an-email", "message": "hi"}, "'not-an-email' is not a 'email'"),
            ({"to": ["foo@foo.com", "nope"], "message": "hi"}, "'nope' is not a 'email'"),
            ({"to": [], "message": "hi"}, "'to': List should have at least 1 item"),
            ({"to": ["foo@foo.com", "foo@foo.com"], "message": "hi"}, "has non-unique elements"),
            ({"to": "foo@foo.com", "message": "hi", "cc": "nope"}, "'nope' is not a 'email'"),
            ({"to": "foo@foo.com", "message": "hi", "from": "nope"}, "'nope' is not a 'email'"),
            ({"to": "foo@foo.com", "message": "hi", "username": "u"}, "'password' is a dependency of 'username'"),
            ({"to": "foo@foo.com", "message": "hi", "password": "p"}, "'username' is a dependency of 'password'"),
            ({"to": "foo@foo.com", "message": "hi", "attachments": "/no/such/file"}, "'/no/such/file' is not a 'valid_file'"),
            ({"to": "foo@foo.com", "message": "hi", "port": 70000}, "'port': Input should be less than or equal to 65535"),
            ({"to": "foo@foo.com", "message": "hi", "port": "abc"}, "'port': Input should be a valid integer"),
            ({"to": "foo@foo.com", "message": 123}, "'message': Input should be a valid string"),
            ({"to": "foo@foo.com", "message": "hi", "foo": "bar"}, "Additional properties are not allowed ('foo' was unexpected)"),
        ],
    )
    def test_invalid_arguments(self, smtp, data, message):
        with pytest.raises(BadArguments) as e:
            self.notify(**data)
        assert message in e.value.message
        assert e.value.provider == self.provider_name
        assert smtp.instances == []

    def test_environment_variables(self, smtp, monkeypatch):
        prefix = f"NOTIFIERS_{self.provider_name.upper()}_"
        monkeypatch.setenv(f"{prefix}TO", "env@foo.com")
        monkeypatch.setenv(f"{prefix}FROM", "envfrom@foo.com")
        monkeypatch.setenv(f"{prefix}USERNAME", "eu")
        monkeypatch.setenv(f"{prefix}PASSWORD", "ep")
        monkeypatch.setenv(f"{prefix}PORT", "2525")
        rsp = self.notify(message="hi")
        assert rsp.ok
        assert (rsp.data["to"], rsp.data["from"], rsp.data["username"], rsp.data["port"]) == ("env@foo.com", "envfrom@foo.com", "eu", 2525)

    def test_env_from_underscore(self, smtp, monkeypatch):
        monkeypatch.setenv(f"NOTIFIERS_{self.provider_name.upper()}_FROM_", "envfrom@foo.com")
        rsp = self.notify(to="foo@foo.com", message="hi")
        assert rsp.data["from"] == "envfrom@foo.com"

    def test_arguments_take_precedence_over_environment(self, smtp, monkeypatch):
        monkeypatch.setenv(f"NOTIFIERS_{self.provider_name.upper()}_TO", "env@foo.com")
        rsp = self.notify(to="arg@foo.com", message="hi")
        assert rsp.data["to"] == "arg@foo.com"

    def test_env_prefix(self, smtp, monkeypatch):
        monkeypatch.setenv(f"MY_PREFIX_{self.provider_name.upper()}_TO", "prefixed@foo.com")
        rsp = self.notify(message="hi", env_prefix="MY_PREFIX_")
        assert rsp.data["to"] == "prefixed@foo.com"

    def test_logging_handler(self, smtp):
        log = logging.getLogger(f"test_email_handler_{self.provider_name}")
        log.propagate = False
        handler = NotificationHandler(self.provider_name, defaults={"to": "foo@foo.com", "subject": "log"})
        handler.setLevel(logging.ERROR)
        log.addHandler(handler)
        try:
            log.error("something broke")
        finally:
            log.removeHandler(handler)
        message = sent_message(smtp)
        assert message["Subject"] == "log"
        assert body(message)[1] == "something broke"


class TestGmail(TestEmail):
    provider_name = "gmail"

    def test_minimal(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi")
        assert rsp.ok
        assert {k: rsp.data[k] for k in ("host", "port", "tls", "ssl", "from")} == {
            "host": "smtp.gmail.com",
            "port": 587,
            "tls": True,
            "ssl": False,
            "from": DEFAULT_FROM,
        }
        (connection,) = smtp.instances
        assert (connection.host, connection.port) == ("smtp.gmail.com", 587)
        assert connection.calls == [("ehlo",), ("starttls",)]

    def test_login(self, smtp):
        self.notify(to="foo@foo.com", message="hi", username="me@gmail.com", password="app-password")
        (connection,) = smtp.instances
        assert connection.calls == [("ehlo",), ("starttls",), ("login", "me@gmail.com", "app-password")]

    def test_port_and_bool_strings_are_coerced(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi", port="2525", username="u", password="p")
        assert rsp.data["port"] == 2525

    def test_defaults(self):
        assert notifiers.get_notifier("gmail").defaults == {
            "subject": DEFAULT_SUBJECT,
            "from": notifiers.providers.email.default_from(),
            "host": "smtp.gmail.com",
            "port": 587,
            "tls": True,
            "ssl": False,
            "html": False,
            "login": True,
        }


class TestICloud(TestEmail):
    provider_name = "icloud"
    credentials = {"username": "me@icloud.com", "password": "app-password"}

    def notify(self, **kwargs):
        if "username" not in kwargs and "password" not in kwargs and not kwargs.get("env_prefix"):
            kwargs = {**self.credentials, **kwargs}
        return notifiers.get_notifier(self.provider_name).notify(**kwargs)

    def test_minimal(self, smtp):
        rsp = self.notify(to="foo@foo.com", message="hi", **{"from": "me@icloud.com"})
        assert rsp.ok
        (connection,) = smtp.instances
        assert (connection.host, connection.port) == ("smtp.mail.me.com", 587)
        assert connection.calls == [("ehlo",), ("starttls",), ("login", "me@icloud.com", "app-password")]
        assert sent_message(smtp)["From"] == "me@icloud.com"

    def test_tls_and_login(self, smtp):
        self.notify(to="foo@foo.com", message="hi", username="u", password="p")
        (connection,) = smtp.instances
        assert connection.calls == [("ehlo",), ("starttls",), ("login", "u", "p")]

    def test_login_false_skips_login(self, smtp):
        self.notify(to="foo@foo.com", message="hi", login=False)
        (connection,) = smtp.instances
        assert all(call[0] != "login" for call in connection.calls)

    @pytest.mark.parametrize("missing", ["username", "password"])
    def test_credentials_are_required(self, smtp, missing):
        data = {"to": "foo@foo.com", "message": "hi", **self.credentials}
        del data[missing]
        with pytest.raises(BadArguments, match=f"'{missing}' is a required property"):
            notifiers.get_notifier("icloud").notify(**data)

    def test_required(self):
        assert notifiers.get_notifier("icloud").required == {"required": ["message", "to", "from", "username", "password"]}

    def test_environment_variables(self, smtp, monkeypatch):
        prefix = "NOTIFIERS_ICLOUD_"
        for key, value in {"TO": "env@foo.com", "FROM": "envfrom@icloud.com", "USERNAME": "eu", "PASSWORD": "ep", "PORT": "2525"}.items():
            monkeypatch.setenv(f"{prefix}{key}", value)
        rsp = notifiers.get_notifier("icloud").notify(message="hi")
        assert rsp.ok
        assert (rsp.data["to"], rsp.data["from"], rsp.data["username"], rsp.data["port"]) == ("env@foo.com", "envfrom@icloud.com", "eu", 2525)

    def test_env_prefix(self, smtp, monkeypatch):
        monkeypatch.setenv("MY_PREFIX_ICLOUD_TO", "prefixed@foo.com")
        rsp = self.notify(message="hi", env_prefix="MY_PREFIX_", **self.credentials)
        assert rsp.data["to"] == "prefixed@foo.com"

    def test_logging_handler(self, smtp):
        log = logging.getLogger("test_email_handler_icloud")
        log.propagate = False
        handler = NotificationHandler("icloud", defaults={"to": "foo@foo.com", "subject": "log", **self.credentials})
        handler.setLevel(logging.ERROR)
        log.addHandler(handler)
        try:
            log.error("something broke")
        finally:
            log.removeHandler(handler)
        assert body(sent_message(smtp))[1] == "something broke"

    @pytest.mark.parametrize(
        ("data", "message"),
        [
            ({"message": "hi"}, "'to' is a required property"),
            ({"to": "foo@foo.com"}, "'message' is a required property"),
            ({"to": "not-an-email", "message": "hi"}, "'not-an-email' is not a 'email'"),
            ({"to": "foo@foo.com", "message": "hi", "foo": "bar"}, "Additional properties are not allowed ('foo' was unexpected)"),
        ],
    )
    def test_invalid_arguments(self, smtp, data, message):
        with pytest.raises(BadArguments) as e:
            self.notify(**data)
        assert message in e.value.message
        assert smtp.instances == []
