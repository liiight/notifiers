from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import notifiers
from notifiers.core import SUCCESS_STATUS, Response
from notifiers.exceptions import BadArguments

# Mark all tests in this file to run with pytest-asyncio
pytestmark = pytest.mark.asyncio


class TestAsyncCore:
    async def test_async_notify_fallback(self, mock_provider):
        """Test that a standard provider without native async support falls back to executor thread"""
        data = {"required": "foo", "not_required": ["foo", "bar"]}
        rsp = await mock_provider.notify_async(**data)
        assert isinstance(rsp, Response)
        assert not rsp.errors
        assert rsp.status == SUCCESS_STATUS

    async def test_top_level_notify_async(self, mock_provider):
        """Test the package-level notify_async function"""
        data = {"required": "foo", "not_required": ["foo", "bar"]}
        rsp = await notifiers.notify_async("mock_provider", **data)
        assert isinstance(rsp, Response)
        assert not rsp.errors
        assert rsp.status == SUCCESS_STATUS

    async def test_async_validation_errors(self, mock_provider):
        """Test that validation schema works synchronously within notify_async"""
        with pytest.raises(BadArguments):
            await mock_provider.notify_async(not_required="foo")

    @patch("notifiers.utils.requests.httpx")
    async def test_slack_native_async(self, mock_httpx):
        """Test Slack's native async implementation using a mocked httpx response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_response.raise_for_status = lambda: None

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = lambda *_, **__: None

        slack = notifiers.get_notifier("slack")
        rsp = await slack.notify_async(webhook_url="https://hooks.slack.com/services/123", message="Hello Async!")
        assert isinstance(rsp, Response)
        assert rsp.status == SUCCESS_STATUS
        assert not rsp.errors

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert args[0].upper() == "POST"
        assert args[1] == "https://hooks.slack.com/services/123"
        assert kwargs["json"]["text"] == "Hello Async!"

    @patch("notifiers.utils.requests.httpx")
    async def test_telegram_native_async(self, mock_httpx):
        """Test Telegram's native async implementation using a mocked httpx response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_response.raise_for_status = lambda: None

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = lambda *_, **__: None

        telegram = notifiers.get_notifier("telegram")
        rsp = await telegram.notify_async(token="123:abc", chat_id="456", message="Hello Async!")
        assert isinstance(rsp, Response)
        assert rsp.status == SUCCESS_STATUS
        assert not rsp.errors

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert args[0].upper() == "POST"
        assert args[1] == "https://api.telegram.org/bot123:abc/sendMessage"
        assert kwargs["json"]["text"] == "Hello Async!"

    @pytest.mark.parametrize(
        ("provider_name", "data", "expected_url", "expected_method"),
        [
            (
                "gitter",
                {"token": "foo", "room_id": "bar", "message": "hello"},
                "https://api.gitter.im/v1/rooms/bar/chatMessages",
                "POST",
            ),
            (
                "mailgun",
                {"api_key": "foo", "domain": "bar", "to": "baz@host.com", "from": "sender@host.com", "message": "hello"},
                "https://api.mailgun.net/v3/bar/messages",
                "POST",
            ),
            (
                "pushover",
                {"token": "foo", "user": "bar", "message": "hello"},
                "https://api.pushover.net/1/messages.json",
                "POST",
            ),
            (
                "twilio",
                {"account_sid": "foo", "auth_token": "bar", "to": "+1234567890", "from": "+1987654321", "message": "hello"},
                "https://api.twilio.com/2010-04-01/Accounts/foo/Messages.json",
                "POST",
            ),
            (
                "zulip",
                {"email": "foo@bar.com", "api_key": "bar", "to": "baz", "domain": "qux", "subject": "hello", "message": "hello"},
                "https://qux.zulipchat.com/api/v1/messages",
                "POST",
            ),
            (
                "pagerduty",
                {"routing_key": "foo", "event_action": "trigger", "source": "bar", "severity": "info", "message": "hello"},
                "https://events.pagerduty.com/v2/enqueue",
                "POST",
            ),
            (
                "pushbullet",
                {"token": "foo", "message": "hello"},
                "https://api.pushbullet.com/v2/pushes",
                "POST",
            ),
            (
                "victorops",
                {"rest_url": "https://foo.com", "message_type": "info", "entity_id": "bar", "entity_display_name": "baz", "message": "hello"},
                "https://foo.com",
                "POST",
            ),
            (
                "popcornnotify",
                {"api_key": "foo", "recipients": "bar@host.com", "message": "hello"},
                "https://popcornnotify.com/notify",
                "POST",
            ),
            (
                "simplepush",
                {"key": "foo", "message": "hello"},
                "https://api.simplepush.io/send",
                "POST",
            ),
            (
                "notify",
                {"base_url": "https://foo.com", "title": "bar", "message": "hello"},
                "https://foo.com/api/notify",
                "POST",
            ),
            (
                "statuspage",
                {"api_key": "foo", "page_id": "bar", "message": "hello"},
                "https://api.statuspage.io/v1//pages/bar/incidents.json",
                "POST",
            ),
            (
                "join",
                {"apikey": "foo", "message": "hello"},
                "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush",
                "GET",
            ),
        ],
    )
    @patch("notifiers.utils.requests.httpx")
    async def test_all_native_async_providers(self, mock_httpx, provider_name, data, expected_url, expected_method):
        """Test native async implementations of HTTP providers using a mocked httpx response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_response.json.return_value = {"ok": True, "result": {}, "success": True, "records": []}
        mock_response.raise_for_status = lambda: None

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = lambda *_, **__: None

        p = notifiers.get_notifier(provider_name)
        rsp = await p.notify_async(**data)
        assert isinstance(rsp, Response)
        assert rsp.status == SUCCESS_STATUS

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert args[0].upper() == expected_method.upper()
        assert args[1] == expected_url
