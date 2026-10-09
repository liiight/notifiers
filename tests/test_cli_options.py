"""Tests for generating CLI options from schema models, and for the CLI with the email based providers"""

from __future__ import annotations

import json
import smtplib
import socket
import subprocess
import sys
from typing import Literal

import click
import pytest
from pydantic import Field

from notifiers.models import Email, FilePath, OneOrMore, SchemaModel, one_or_more
from notifiers.providers import email as email_provider
from notifiers_cli.utils.dynamic_click import clean_data, field_to_click_type, params_factory


class _Nested(SchemaModel):
    a: str


class _Schema(SchemaModel):
    message: str
    text: str = Field(description="some text")
    number: int | None = Field(None, description="a number")
    ratio: float | None = None
    flag: bool | None = Field(None, description="a flag")
    choice: Literal["a", "b"] | None = None
    bool_or_choice: Literal[True, False, "htmlonly"] | None = None
    many: OneOrMore[str] | None = Field(None, description="one or more")
    many_emails: one_or_more(Email) | None = None
    files: OneOrMore[FilePath] | None = None
    str_or_int: str | int | None = None
    from_: str | None = Field(None, alias="from")
    device_id: str | None = Field(None, alias="deviceId")
    type_: Literal["x", "y"] = Field("x", alias="type")
    mapping: dict[str, str] | None = None
    nested: _Nested | None = None
    items: list[_Nested] | None = None
    plain_list: list[str] | None = None


def _options() -> dict[str, click.Parameter]:
    return {p.name: p for p in params_factory(_Schema, add_message=True)}


class TestParamsFactory:
    def test_message_is_an_optional_argument(self):
        message = params_factory(_Schema, add_message=True)[0]
        assert isinstance(message, click.Argument)
        assert message.name == "message"
        assert not message.required
        assert all(p.name != "message" for p in params_factory(_Schema, add_message=False))

    @pytest.mark.parametrize(
        ("name", "opts", "click_type", "multiple"),
        [
            ("text", ["--text"], click.STRING, False),
            ("number", ["--number"], click.INT, False),
            ("ratio", ["--ratio"], click.FLOAT, False),
            ("many", ["--many"], click.STRING, True),
            ("many_emails", ["--many-emails"], click.STRING, True),
            ("files", ["--files"], click.STRING, True),
            ("str_or_int", ["--str-or-int"], click.STRING, False),
            ("from", ["--from"], click.STRING, False),
            ("deviceId", ["--deviceId", "--device-id"], click.STRING, False),
        ],
    )
    def test_options(self, name, opts, click_type, multiple):
        option = _options()[name]
        assert option.opts == opts
        assert option.type == click_type
        assert option.multiple is multiple

    def test_bool_flag(self):
        option = _options()["flag"]
        assert option.is_flag
        assert (option.opts, option.secondary_opts) == (["--flag"], ["--no-flag"])
        # Not passing a flag must not send a value
        assert option.default is None

    def test_choices(self):
        options = _options()
        assert list(options["choice"].type.choices) == ["a", "b"]
        assert list(options["bool_or_choice"].type.choices) == ["htmlonly"]
        assert options["type"].opts == ["--type"]
        assert list(options["type"].type.choices) == ["x", "y"]

    def test_unsupported_fields_are_skipped(self):
        assert {"mapping", "nested", "items"}.isdisjoint(_options())

    def test_plain_list_is_multiple(self):
        option = _options()["plain_list"]
        assert (option.type, option.multiple) == (click.STRING, True)

    def test_help(self):
        options = _options()
        assert options["text"].help == "Some text"
        assert options["many"].help == "One or more. Multiple usages of this option are allowed"
        assert options["ratio"].help is None

    def test_field_to_click_type_none_for_complex(self):
        assert field_to_click_type(_Schema.model_fields["mapping"]) is None


def test_clean_data():
    assert clean_data({"a": None, "b": (), "c": ("x", "y"), "d": False, "e": "", "f": 0, "g": "v"}) == {"c": ["x", "y"], "d": False, "f": 0, "g": "v"}


class _FakeSMTP:
    instances: list[_FakeSMTP] = []

    def __init__(self, host, port):
        self.host, self.port, self.calls, self.sent = host, port, [], []
        type(self).instances.append(self)

    def ehlo(self):
        self.calls.append("ehlo")

    def starttls(self):
        self.calls.append("starttls")

    def login(self, username, password):
        self.calls.append(("login", username, password))

    def send_message(self, message):
        self.sent.append(message)


class _FakeSMTPSSL(_FakeSMTP):
    pass


@pytest.fixture
def smtp(monkeypatch):
    _FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", _FakeSMTPSSL)
    monkeypatch.setattr(socket, "getfqdn", lambda *_: "example.test")
    email_provider.default_from.cache_clear()
    yield _FakeSMTP
    email_provider.default_from.cache_clear()


def _sent(smtp):
    (connection,) = smtp.instances
    (message,) = connection.sent
    return connection, message


class TestEmailCLI:
    def test_notify_help(self, cli_runner):
        result = cli_runner(["email", "notify", "--help"])
        assert not result.exit_code
        for option in ["--to", "--cc", "--bcc", "--from", "--subject", "--attachments", "--host", "--port", "--username", "--password"]:
            assert option in result.output
        for flag in ["tls", "ssl", "html", "login"]:
            assert f"--{flag} / --no-{flag}" in result.output
        assert "Multiple usages of this option are" in " ".join(result.output.split())
        assert "[MESSAGE]" in result.output

    def test_notify(self, cli_runner, smtp):
        result = cli_runner(["email", "notify", "--to", "foo@foo.com", "--subject", "Hi", "--from", "me@foo.com", "hello"])
        assert not result.exit_code, result.output
        assert "Succesfully sent a notification to email!" in result.output
        connection, message = _sent(smtp)
        assert (connection.host, connection.port, connection.calls) == ("localhost", 25, [])
        assert (message["To"], message["From"], message["Subject"]) == ("foo@foo.com", "me@foo.com", "Hi")
        assert message.get_body().get_content().strip() == "hello"

    def test_multiple_recipients_and_attachments(self, cli_runner, smtp, tmp_path):
        files = []
        for name in ("a.txt", "b.pdf"):
            (tmp_path / name).write_text("x")
            files.append(str(tmp_path / name))
        cmd = ["email", "notify", "--to", "a@foo.com", "--to", "b@foo.com", "--cc", "c@foo.com", "--attachments", files[0], "--attachments", files[1], "hi"]
        result = cli_runner(cmd)
        assert not result.exit_code, result.output
        _, message = _sent(smtp)
        assert message["To"] == "a@foo.com, b@foo.com"
        assert message["CC"] == "c@foo.com"
        assert [a.get_filename() for a in message.iter_attachments()] == ["a.txt", "b.pdf"]

    def test_tls_login_and_port(self, cli_runner, smtp):
        cmd = ["email", "notify", "--to", "a@foo.com", "--host", "smtp.foo.com", "--port", "587", "--tls", "--username", "u", "--password", "p", "hi"]
        result = cli_runner(cmd)
        assert not result.exit_code, result.output
        connection, _ = _sent(smtp)
        assert (connection.host, connection.port) == ("smtp.foo.com", 587)
        assert connection.calls == ["ehlo", "starttls", ("login", "u", "p")]

    def test_no_flags_keep_defaults(self, cli_runner, smtp):
        """Flags that aren't passed don't override defaults, e.g. gmail's tls=True"""
        result = cli_runner(["gmail", "notify", "--to", "a@foo.com", "hi"])
        assert not result.exit_code, result.output
        connection, _ = _sent(smtp)
        assert (connection.host, connection.port, connection.calls) == ("smtp.gmail.com", 587, ["ehlo", "starttls"])

    def test_negative_flag(self, cli_runner, smtp):
        result = cli_runner(["gmail", "notify", "--to", "a@foo.com", "--no-tls", "--no-login", "hi"])
        assert not result.exit_code, result.output
        connection, _ = _sent(smtp)
        assert connection.calls == []

    def test_html(self, cli_runner, smtp):
        result = cli_runner(["email", "notify", "--to", "a@foo.com", "--html", "<b>hi</b>"])
        assert not result.exit_code, result.output
        _, message = _sent(smtp)
        assert message.get_body().get_content_type() == "text/html"

    def test_piped_message(self, cli_runner, smtp):
        result = cli_runner(["email", "notify", "--to", "a@foo.com"], input="piped message")
        assert not result.exit_code, result.output
        _, message = _sent(smtp)
        assert message.get_body().get_content().strip() == "piped message"

    def test_environment_variables(self, cli_runner, smtp, monkeypatch):
        monkeypatch.setenv("NOTIFIERS_GMAIL_TO", "env@foo.com")
        monkeypatch.setenv("NOTIFIERS_GMAIL_USERNAME", "u")
        monkeypatch.setenv("NOTIFIERS_GMAIL_PASSWORD", "p")
        result = cli_runner(["gmail", "notify", "hi"])
        assert not result.exit_code, result.output
        connection, message = _sent(smtp)
        assert message["To"] == "env@foo.com"
        assert ("login", "u", "p") in connection.calls

    def test_env_prefix(self, cli_runner, smtp, monkeypatch):
        monkeypatch.setenv("MY_EMAIL_TO", "prefixed@foo.com")
        result = cli_runner(["--env-prefix", "MY_", "email", "notify", "hi"])
        assert not result.exit_code, result.output
        _, message = _sent(smtp)
        assert message["To"] == "prefixed@foo.com"

    @pytest.mark.parametrize(
        ("cmd", "error"),
        [
            (["email", "notify", "hi"], "'to' is a required property"),
            (["email", "notify", "--to", "nope", "hi"], "'nope' is not a 'email'"),
            (["email", "notify", "--to", "a@foo.com", "--username", "u", "hi"], "'password' is a dependency of 'username'"),
            (["icloud", "notify", "--to", "a@foo.com", "hi"], "'username' is a required property"),
        ],
    )
    def test_invalid_arguments(self, cli_runner, smtp, cmd, error):
        result = cli_runner(cmd)
        assert result.exit_code
        assert error in str(result.exception)
        assert smtp.instances == []

    def test_bad_port_is_rejected_by_click(self, cli_runner, smtp):
        result = cli_runner(["email", "notify", "--to", "a@foo.com", "--port", "abc", "hi"])
        assert result.exit_code == 2
        assert "'abc' is not a valid integer" in result.output

    def test_core_commands(self, cli_runner):
        result = cli_runner(["gmail", "defaults"])
        assert not result.exit_code
        defaults = json.loads(result.output)
        assert {k: defaults[k] for k in ("host", "port", "tls")} == {"host": "smtp.gmail.com", "port": 587, "tls": True}

        result = cli_runner(["icloud", "required"])
        assert json.loads(result.output) == {"required": ["message", "to", "from", "username", "password"]}

        result = cli_runner(["email", "schema", "--pretty"])
        schema = json.loads(result.output)
        assert schema["title"] == "SMTPSchema"
        assert "from" in schema["properties"]

        result = cli_runner(["email", "metadata"])
        assert json.loads(result.output) == {"base_url": None, "site_url": "https://en.wikipedia.org/wiki/Email", "name": "email"}


class TestJoinCLIAliases:
    @pytest.mark.parametrize("option", ["--deviceId", "--device-id"])
    def test_both_spellings(self, cli_runner, monkeypatch, option):
        captured = {}

        def fake_request(_url, data):
            captured.update(data)
            return None, None

        from notifiers.providers import join  # noqa: PLC0415

        monkeypatch.setattr(join.JoinMixin, "_join_request", staticmethod(fake_request))
        result = cli_runner(["join", "notify", "--apikey", "k", option, "phone", "hi"])
        assert not result.exit_code, result.output
        assert captured == {"apikey": "k", "deviceId": "phone", "text": "hi"}


class TestLazyGroups:
    def test_help_lists_all_providers(self, cli_runner):
        import notifiers  # noqa: PLC0415

        result = cli_runner(["--help"])
        assert not result.exit_code
        for provider in notifiers.all_providers():
            assert provider in result.output
        assert "providers" in result.output

    def test_unknown_command(self, cli_runner):
        result = cli_runner(["nope"])
        assert result.exit_code == 2
        assert "No such command 'nope'" in result.output

    def test_only_invoked_provider_is_built(self):
        code = (
            "import sys\n"
            "from unittest.mock import patch\n"
            "from notifiers_cli import core\n"
            "built = []\n"
            "original = core.provider_group\n"
            "def tracking(name):\n"
            "    built.append(name)\n"
            "    return original(name)\n"
            "core.provider_group = tracking\n"
            "sys.argv = ['notifiers', 'email', 'notify', '--help']\n"
            "try:\n"
            "    core.entry_point()\n"
            "except SystemExit:\n"
            "    pass\n"
            "print('BUILT', built)\n"
        )
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        assert "BUILT ['email']" in result.stdout
