import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


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
        assert f"'{message}' is a required property" in e.value.message

    def test_bad_token(self):
        p = get_notifier('telegram')
        data = {
            'token': 'foo',
            'chat_id': 1,
            'message': 'foo'
        }
        with pytest.raises(NotificationError) as e:
            rsp = p.notify(**data)
            rsp.raise_on_errors()
        assert 'Not Found' in e.value.message

    @pytest.mark.online
    def test_missing_chat_id(self):
        p = get_notifier('telegram')
        data = {
            'chat_id': 1,
            'message': 'foo'
        }
        with pytest.raises(NotificationError) as e:
            rsp = p.notify(**data)
            rsp.raise_on_errors()
        assert 'chat not found' in e.value.message

    @pytest.mark.online
    def test_sanity(self):
        p = get_notifier('telegram')
        rsp = p.notify(message='foo')
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self):
        p = get_notifier('telegram')
        data = {
            'parse_mode': 'markdown',
            'disable_web_page_preview': True,
            'disable_notification': True,
            'message': '_foo_'
        }
        rsp = p.notify(**data)
        rsp.raise_on_errors()
