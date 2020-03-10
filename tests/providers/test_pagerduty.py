import datetime

import pytest

from notifiers.exceptions import BadArguments

provider = "pagerduty"


class TestPagerDuty:
    @pytest.mark.parametrize(
        "data, message",
        [
            ({}, "routing_key"),
            ({"routing_key": "foo"}, "event_action"),
            ({"routing_key": "foo", "event_action": "trigger"}, "source"),
            (
                {"routing_key": "foo", "event_action": "trigger", "source": "foo"},
                "severity",
            ),
            (
                {
                    "routing_key": "foo",
                    "event_action": "trigger",
                    "source": "foo",
                    "severity": "info",
                },
                "message",
            ),
        ],
    )
    def test_pagerduty_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_pagerduty_sanity(self, provider, test_message):
        data = {
            "message": test_message,
            "event_action": "trigger",
            "source": "foo",
            "severity": "info",
        }
        rsp = provider.notify(**data, raise_on_errors=True)
        raw_rsp = rsp.response.json()
        del raw_rsp["dedup_key"]
        assert raw_rsp == {"status": "success", "message": "Event processed"}

    @pytest.mark.online
    def test_pagerduty_all_options(self, provider, test_message):
        images = [
            {
                "src": "https://software.opensuse.org/package/thumbnail/python-Pillow.png",
                "href": "https://github.com/liiight/notifiers",
                "alt": "Notifiers",
            }
        ]
        links = [
            {
                "href": "https://github.com/notifiers/notifiers",
                "text": "Python Notifiers",
            }
        ]
        data = {
            "message": test_message,
            "event_action": "trigger",
            "source": "bar",
            "severity": "info",
            "timestamp": datetime.datetime.now().isoformat(),
            "component": "baz",
            "group": "bla",
            "class": "buzu",
            "custom_details": {"foo": "bar", "boo": "yikes"},
            "images": images,
            "links": links,
        }
        rsp = provider.notify(**data, raise_on_errors=True)
        raw_rsp = rsp.response.json()
        del raw_rsp["dedup_key"]
        assert raw_rsp == {"status": "success", "message": "Event processed"}
