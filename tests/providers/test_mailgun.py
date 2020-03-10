import datetime

import pytest

from notifiers.exceptions import BadArguments
from notifiers.models.response import ResponseStatus

provider = "mailgun"


class TestMailgun:
    @pytest.mark.parametrize(
        "data, message",
        [
            ({}, "Either 'text' or 'html' are required"),
            ({"message": "foo"}, "api_key\n  field required"),
            (
                {"message": "foo", "to": "non-email"},
                "to\n  value is not a valid email address",
            ),
            (
                {"message": "foo", "to": "1@1.com", "api_key": "foo"},
                "domain\n  field required",
            ),
            (
                {"message": "foo", "to": "1@1.com", "api_key": "foo", "domain": "foo"},
                "from\n  field required",
            ),
        ],
    )
    def test_mailgun_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments, match=message):
            provider.notify(**data)

    @pytest.mark.online
    def test_mailgun_sanity(self, provider, test_message):
        provider.notify(message=test_message, raise_on_errors=True)

    @pytest.mark.online
    def test_mailgun_all_options(self, provider, tmpdir, test_message):
        dir_ = tmpdir.mkdir("sub")
        file_1 = dir_.join("hello.txt")
        file_1.write("content")

        file_2 = dir_.join("world.txt")
        file_2.write("content")

        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        data = {
            "message": test_message,
            "html": f"<b>{now}</b>",
            "subject": f"{now}",
            "attachment": [file_1.strpath, file_2.strpath],
            "inline": [file_1.strpath, file_2.strpath],
            "tag": ["foo", "bar"],
            "dkim": True,
            "delivery_time": now,
            "test_mode": False,
            "tracking": True,
            "tracking_clicks": "htmlonly",
            "tracking_opens": True,
            "require_tls": False,
            "skip_verification": True,
            "headers": {"foo": "bar"},
            "data": {"foo": {"bar": "bla"}},
        }
        provider.notify(**data, raise_on_errors=True)

    def test_mailgun_error_response(self, provider):
        data = {
            "api_key": "FOO",
            "message": "bla",
            "to": "foo@foo.com",
            "domain": "foo",
            "from": "foo@foo.com",
        }
        rsp = provider.notify(**data)
        assert rsp.status is ResponseStatus.FAILURE
        assert "Forbidden" in rsp.errors
