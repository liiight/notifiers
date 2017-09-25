import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments


class TestTelegram:
    """
    Telegram related tests
    """

    def test_metadata(self):
        t = get_notifier('telegram')
        assert t.metadata == {
            'base_url': 'https://api.telegram.org/bot{token}/{method}',
            'provider_name': 'telegram',
            'site_url': 'https://core.telegram.org/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'chat_id'),
        ({'message': 'foo', 'chat_id': 1}, 'token'),
    ])
    def test_missing_required(self, data, message):
        p = get_notifier('telegram')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f'\'{message}\' is a required property' in e.value.message
