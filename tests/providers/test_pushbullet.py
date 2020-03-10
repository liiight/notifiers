import os

import pytest

from notifiers.exceptions import BadArguments

provider = "pushbullet"


@pytest.mark.skip(reason="Re-enable once account is activated again")
class TestPushbullet:
    @pytest.mark.parametrize(
        "data, message", [({}, "message"), ({"message": "foo"}, "token")]
    )
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
        assert provider.devices()


@pytest.mark.skip("Provider resources CLI command are not ready yet")
class TestPushbulletCLI:
    """Test Pushbullet specific CLI"""

    def test_pushbullet_devices_negative(self, cli_runner):
        cmd = "pushbullet devices --token bad_token".split()
        result = cli_runner(cmd)
        assert result.exit_code
        assert not result.output

    @pytest.mark.online
    def test_pushbullet_devices_positive(self, cli_runner):
        token = os.environ.get("NOTIFIERS_PUSHBULLET_TOKEN")
        assert token

        cmd = f"pushbullet devices --token {token}".split()
        result = cli_runner(cmd)
        assert not result.exit_code
        replies = ["You have no devices associated with this token", "Nickname: "]
        assert any(reply in result.output for reply in replies)
