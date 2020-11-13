import json

import pytest
from retry import retry

from notifiers.exceptions import NotificationError
from notifiers.exceptions import SchemaValidationError

provider = "telegram"


class TestTelegram:
    """Telegram related tests"""

    def test_bad_token(self, provider):
        data = {"token": "foo", "chat_id": 1, "message": "foo"}
        with pytest.raises(NotificationError) as e:
            rsp = provider.notify(**data)
            rsp.raise_on_errors()
        assert "Not Found" in e.value.message

    @pytest.mark.online
    def test_missing_chat_id(self, provider):
        data = {"chat_id": 1, "message": "foo"}
        with pytest.raises(NotificationError) as e:
            rsp = provider.notify(**data)
            rsp.raise_on_errors()
        assert "chat not found" in e.value.message

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        rsp = provider.notify(message=test_message)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self, provider, test_message):
        data = {
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
            "disable_notification": True,
            "message": test_message,
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()


class TestTelegramResources:
    resource = "updates"

    def test_telegram_updates_attribs(self, resource):
        assert resource.schema() == {
            "additionalProperties": False,
            "description": "The base class for Schemas",
            "properties": {
                "token": {
                    "description": "Bot token",
                    "title": "Token",
                    "type": "string",
                }
            },
            "required": ["token"],
            "title": "TelegramBaseSchema",
            "type": "object",
        }
        assert resource.name == provider
        assert resource.required == ["token"]

    def test_telegram_updates_negative(self, resource):
        with pytest.raises(SchemaValidationError):
            resource(env_prefix="foo")

    @pytest.mark.online
    def test_telegram_updates_positive(self, resource):
        rsp = resource()
        assert isinstance(rsp, list)


class TestTelegramCLI:
    """Test telegram specific CLI"""

    def test_telegram_updates_negative(self, cli_runner):
        cmd = "telegram updates --token bad_token".split()
        result = cli_runner(cmd)
        assert result.exit_code
        assert not result.output

    @pytest.mark.online
    @retry(AssertionError, tries=3, delay=10)
    def test_telegram_updates_positive(self, cli_runner):
        cmd = "telegram updates".split()
        result = cli_runner(cmd)
        assert not result.exit_code
        reply = json.loads(result.output)
        assert reply == [] or reply[0]["message"]["chat"]["id"]
