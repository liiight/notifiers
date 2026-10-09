import socket
import subprocess
import sys
from email.message import EmailMessage
from unittest.mock import MagicMock

import pytest

from notifiers.exceptions import BadArguments, NotificationError
from notifiers.providers import email

provider = "email"


class TestSMTP:
    """SMTP tests"""

    def test_smtp_metadata(self, provider):
        assert provider.metadata == {
            "base_url": None,
            "name": "email",
            "site_url": "https://en.wikipedia.org/wiki/Email",
        }

    @pytest.mark.parametrize(("data", "message"), [({}, "message"), ({"message": "foo"}, "to")])
    def test_smtp_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_smtp_no_host(self, provider):
        data = {
            "to": "foo@foo.com",
            "message": "bar",
            "host": "nohost",
            "username": "ding",
            "password": "dong",
        }
        rsp = provider.notify(**data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        possible_errors = "Errno 111", "Errno 61", "Errno 8", "Errno -2", "Errno -3"
        assert any(error in e.value.message for error in possible_errors), f"Error not in expected errors; {e.value.message}"
        assert any(error in rsp_error for rsp_error in rsp.errors for error in possible_errors), f"Error not in expected errors; {rsp.errors}"

    def test_email_from_key(self, provider):
        rsp = provider.notify(
            to="foo@foo.co ",
            from_="bla@foo.com",
            message="foo",
            host="nohost",
            username="ding",
            password="dong",
        )
        rsp_data = rsp.data
        assert not rsp_data.get("from_")
        assert rsp_data["from"] == "bla@foo.com"

    def test_multiple_to(self, provider):
        to = ["foo@foo.com", "bar@foo.com"]
        rsp = provider.notify(to=to, message="foo", host="nohost", username="ding", password="dong")
        assert rsp.data["to"] == ",".join(to)

    def test_attachment(self, provider, tmpdir):
        dir_ = tmpdir.mkdir("sub")
        file_1 = dir_.join("foo.txt")
        file_1.write("foo")
        file_2 = dir_.join("bar.txt")
        file_2.write("foo")
        file_3 = dir_.join("baz.txt")
        file_3.write("foo")
        attachments = [str(file_1), str(file_2), str(file_3)]
        rsp = provider.notify(
            to=["foo@foo.com"],
            message="bar",
            attachments=attachments,
            host="nohost",
            username="ding",
            password="dong",
        )
        assert rsp.data["attachments"] == attachments

    def test_attachment_mimetypes(self, provider, tmpdir):
        dir_ = tmpdir.mkdir("sub")
        file_1 = dir_.join("foo.txt")
        file_1.write("foo")
        file_2 = dir_.join("bar.jpg")
        file_2.write("foo")
        file_3 = dir_.join("baz.pdf")
        file_3.write("foo")
        attachments = [str(file_1), str(file_2), str(file_3)]
        email = EmailMessage()
        provider._add_attachments(attachments=attachments, email=email)
        attach1, attach2, attach3 = email.iter_attachments()
        assert attach1.get_content_type() == "text/plain"
        assert attach2.get_content_type() == "image/jpeg"
        assert attach3.get_content_type() == "application/pdf"

    @pytest.mark.online
    @pytest.mark.skip(reason="Disabled account")
    def test_smtp_sanity(self, provider, test_message):
        """using Gmail SMTP"""
        data = {
            "message": f"<b>{test_message}</b>",
            "host": "smtp.gmail.com",
            "port": 465,
            "ssl": True,
            "html": True,
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()


class TestDefaultFromIsLazy:
    """The default FROM address needs a hostname lookup, which can block for seconds (#483)"""

    def test_import_does_not_resolve_hostname(self):
        code = (
            "from unittest.mock import patch\n"
            "with patch('socket.getfqdn', return_value='example.test') as lookup:\n"
            "    import notifiers\n"
            "    from notifiers.providers.telegram import Telegram\n"
            "    notifiers.get_notifier('email').schema\n"
            "    print(lookup.call_count)\n"
        )
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        assert result.stdout.strip() == "0"

    def test_explicit_from_does_not_resolve_hostname(self, provider, monkeypatch):
        lookup = MagicMock(return_value="example.test")
        monkeypatch.setattr(socket, "getfqdn", lookup)
        email.default_from.cache_clear()
        data = provider._process_data(to="foo@foo.com", message="bar", **{"from": "bla@foo.com"})
        assert data["from"] == "bla@foo.com"
        lookup.assert_not_called()

    def test_default_from(self, provider, monkeypatch):
        monkeypatch.setattr(socket, "getfqdn", MagicMock(return_value="example.test"))
        email.default_from.cache_clear()
        try:
            assert provider._process_data(to="foo@foo.com", message="bar")["from"] == "notifiers@example.test"
        finally:
            email.default_from.cache_clear()
