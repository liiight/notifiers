import pytest
import json

from notifiers.exceptions import BadArguments, NotificationError

provider = 'telegram'


class TestTelegram:
    """Telegram related tests"""

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
    resource = 'updates'

    def test_telegram_updates_attribs(self, resource):
        assert resource.schema == {
            'additionalProperties': False,
            'properties': {'token': {'title': 'Bot token', 'type': 'string'}},
            'required': ['token'],
            'type': 'object'
        }
        assert resource.name == provider
        assert resource.required == {'required': ['token']}

    def test_telegram_updates_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix='foo')

    @pytest.mark.online
    def test_telegram_updates_positive(self, resource):
        rsp = resource()
        assert isinstance(rsp, list)


class TestTelegramCLI:
    """Test telegram specific CLI"""

    def test_telegram_updates_negative(self, cli_runner):
        cmd = 'telegram updates --token bad_token'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output

    @pytest.mark.online
    def test_telegram_updates_positive(self, cli_runner):
        cmd = f'telegram updates'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        reply = json.loads(result.output)
        assert reply == [] or reply[0]['message']['chat']['id']
