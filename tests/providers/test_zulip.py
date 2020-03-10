import datetime

import pytest

from notifiers.exceptions import BadArguments
from notifiers.exceptions import NotifierException

provider = "zulip"


class TestZulip:
    @pytest.mark.parametrize(
        "data, message",
        [
            (
                {"email": "foo", "api_key": "bar", "message": "boo", "to": "bla"},
                "domain",
            ),
            (
                {
                    "email": "foo",
                    "api_key": "bar",
                    "message": "boo",
                    "to": "bla",
                    "domain": "bla",
                    "server": "fop",
                },
                "Only one of 'domain' or 'server' is allowed",
            ),
        ],
    )
    def test_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert message in e.value.message

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {
            "to": "general",
            "message": test_message,
            "domain": "notifiers",
            "subject": "test",
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_private_message(self, provider):
        data = {
            "message": str(datetime.datetime.now()),
            "domain": "notifiers",
            "type": "private",
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_zulip_type_key(self, provider):
        rsp = provider.notify(
            email="foo@foo.com",
            api_key="bar",
            to="baz",
            domain="bla",
            type_="private",
            message="foo",
            subject="foo",
        )
        rsp_data = rsp.data
        assert not rsp_data.get("type_")
        assert rsp_data["type"] == "private"

    def test_zulip_missing_subject(self, provider):
        with pytest.raises(NotifierException) as e:
            provider.notify(
                email="foo@foo.com",
                api_key="bar",
                to="baz@foo.com",
                domain="bla",
                type_="stream",
                message="foo",
            )
        assert "'subject' is required when 'type' is 'stream'" in e.value.message
