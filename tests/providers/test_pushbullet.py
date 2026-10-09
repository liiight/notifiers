import json
import os

import pytest

from notifiers.exceptions import BadArguments

provider = "pushbullet"


class TestPushbullet:
    def test_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "https://api.pushbullet.com/v2/pushes",
            "name": "pushbullet",
            "site_url": "https://www.pushbullet.com",
        }

    @pytest.mark.parametrize(("data", "message"), [({}, "message"), ({"message": "foo"}, "token")])
    def test_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {"message": test_message}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self, provider, test_message):
        data = {
            "message": test_message,
            "type": "link",
            "url": "https://google.com",
            "title": "❤",
            # todo add the rest
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_pushbullet_devices(self, provider):
        assert isinstance(provider.devices(), list)


class TestPushbulletCLI:
    """Test Pushbullet specific CLI"""

    def test_pushbullet_devices_negative(self, cli_runner):
        cmd = ["pushbullet", "devices", "--token", "bad_token"]
        result = cli_runner(cmd)
        assert result.exit_code
        assert not result.output

    @pytest.mark.online
    def test_pushbullet_devices_positive(self, cli_runner):
        token = os.environ.get("NOTIFIERS_PUSHBULLET_TOKEN")
        assert token

        cmd = ["pushbullet", "devices", "--token", token]
        result = cli_runner(cmd)
        assert not result.exit_code, result.output
        assert isinstance(json.loads(result.output), list)
