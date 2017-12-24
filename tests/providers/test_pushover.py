import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestPushover(object):
    """Pushover notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_PUSHOVER_TOKEN and NOTIFIERS_PUSHOVER_USER
    """

    def test_pushover_metadata(self):
        p = get_notifier('pushover')
        assert {'base_url': 'https://api.pushover.net/1/messages.json', 'site_url': 'https://pushover.net/',
                'provider_name': 'pushover',
                'sounds': ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan',
                           'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm',
                           'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']
                } == p.metadata

    @pytest.mark.parametrize('data, message', [
        ({}, 'user'),
        ({'user': 'foo'}, 'message'),
        ({'user': 'foo', 'message': 'bla'}, 'token')
    ])
    def test_missing_required(self, data, message):
        p = get_notifier('pushover')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.parametrize('data, message', [
        ({}, 'expire'),
        ({'expire': 30}, 'retry'),
    ])
    @pytest.mark.online
    def test_pushover_priority_2_restrictions(self, data, message):
        """Pushover specific API restrictions when using priority 2"""
        p = get_notifier('pushover')
        base_data = {'message': 'foo',
                     'priority': 2}
        final_data = {**base_data, **data}
        rsp = p.notify(**final_data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()
        print(e.value.message)
        assert message in e.value.message

    @pytest.mark.online
    def test_sanity(self):
        """Successful pushover notification"""
        p = get_notifier('pushover')
        data = {'message': 'foo'}
        rsp = p.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self):
        """Use all available pushover options"""
        p = get_notifier('pushover')
        data = {'message': 'foo',
                'title': 'title',
                'priority': 2,
                'url': 'http://foo.com',
                'url_title': 'url title',
                'sound': 'bike',
                'timestamp': 0,
                'retry': 30,
                'expire': 30,
                'callback': 'http://callback.com',
                'html': 1}
        rsp = p.notify(**data)
        rsp.raise_on_errors()
