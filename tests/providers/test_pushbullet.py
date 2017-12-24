import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments


class TestPushbullet:
    def test_metadata(self):
        p = get_notifier('pushbullet')
        assert p.metadata == {
            'base_url': 'https://api.pushbullet.com/v2/pushes',
            'provider_name': 'pushbullet',
            'site_url': 'https://www.pushbullet.com'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'token'),
    ])
    def test_missing_required(self, data, message):
        p = get_notifier('pushbullet')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.skip('Account is inactive for over a month, figure out how to get around this')
    @pytest.mark.online
    def test_sanity(self):
        p = get_notifier('pushbullet')
        data = {'message': 'foo'}
        rsp = p.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.skip('Account is inactive for over a month, figure out how to get around this')
    @pytest.mark.online
    def test_all_options(self):
        p = get_notifier('pushbullet')
        data = {
            'message': 'foo',
            'type': 'link',
            'url': 'https://google.com',
            'title': '❤',
            # todo add the rest
        }
        rsp = p.notify(**data)
        rsp.raise_on_errors()
