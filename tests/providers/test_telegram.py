import os

import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestTelegram:
    """Telegram related tests"""

    provider = 'telegram'

    def test_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://api.telegram.org/bot{token}',
            'name': 'telegram',
            'site_url': 'https://core.telegram.org/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'chat_id'),
        ({'message': 'foo', 'chat_id': 1}, 'token'),
    ])
    def test_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    def test_bad_token(self, provider):
        data = {
            'token': 'foo',
            'chat_id': 1,
            'message': 'foo'
        }
        with pytest.raises(NotificationError) as e:
            rsp = provider.notify(**data)
            rsp.raise_on_errors()
        assert 'Not Found' in e.value.message

    @pytest.mark.online
    def test_missing_chat_id(self, provider):
        data = {
            'chat_id': 1,
            'message': 'foo'
        }
        with pytest.raises(NotificationError) as e:
            rsp = provider.notify(**data)
            rsp.raise_on_errors()
        assert 'chat not found' in e.value.message

    @pytest.mark.online
    def test_sanity(self, provider):
        rsp = provider.notify(message='foo')
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self, provider):
        data = {
            'parse_mode': 'markdown',
            'disable_web_page_preview': True,
            'disable_notification': True,
            'message': '_foo_'
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()


class TestTelegramResources:
    provider = 'telegram'
    resource = 'updates'

    def test_telegram_updates_attribs(self, resource):
        assert resource.schema == {
            'additionalProperties': False,
            'properties': {'token': {'title': 'Bot token', 'type': 'string'}},
            'required': ['token'],
            'type': 'object'
        }
        assert resource.name == self.provider
        assert resource.required == {'required': ['token']}

    def test_telegram_updates_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix='foo')

    @pytest.mark.online
    def test_telegram_updates_positive(self, resource):
        rsp = resource()
        assert isinstance(rsp, list)


@pytest.mark.skip('Provider resources CLI command are not ready yet')
class TestTelegramCLI:
    """Test telegram specific CLI"""

    def test_telegram_updates_negative(self, cli_runner):
        cmd = 'telegram updates --token bad_token'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output

    @pytest.mark.online
    def test_telegram_updates_positive(self, cli_runner):
        token = os.environ.get('NOTIFIERS_TELEGRAM_TOKEN')
        assert token

        cmd = f'telegram updates --token {token}'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        replies = ['Bot has not active chats! Send it ANY message and try again', 'Chat ID:']
        assert any(reply in result.output for reply in replies)
