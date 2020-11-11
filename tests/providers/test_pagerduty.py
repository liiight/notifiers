import datetime

import pytest

provider = "pagerduty"


class TestPagerDuty:
    @pytest.mark.online
    def test_pagerduty_sanity(self, provider, test_message):
        data = {
            "event_action": "trigger",
            "payload": {"message": test_message, "source": "foo", "severity": "info"},
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
            "payload": {
                "message": test_message,
                "source": "bar",
                "severity": "info",
                "timestamp": datetime.datetime.now(),
                "component": "baz",
                "group": "bla",
                "class": "buzu",
                "custom_details": {"foo": "bar", "boo": "yikes"},
            },
            "event_action": "trigger",
            "images": images,
            "links": links,
        }
        rsp = provider.notify(**data, raise_on_errors=True)
        raw_rsp = rsp.response.json()
        del raw_rsp["dedup_key"]
        assert raw_rsp == {"status": "success", "message": "Event processed"}
