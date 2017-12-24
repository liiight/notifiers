import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments


class TestSimplePush(object):
    """SimplePush notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_SIMPLEPUSH_KEY
    """

    def test_simplepush_metadata(self):
        p = get_notifier('simplepush')
        assert p.metadata == {'base_url': 'https://api.simplepush.io/send',
                              'site_url': 'https://simplepush.io/',
                              'provider_name': 'simplepush'}

    @pytest.mark.parametrize('data, message', [
        ({}, 'key'),
        ({'key': 'foo'}, 'message'),
    ])
    def test_simplepush_missing_required(self, data, message):
        p = get_notifier('simplepush')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_simplepush_sanity(self):
        """Successful simplepush notification"""
        p = get_notifier('simplepush')
        data = {'message': 'foo'}
        rsp = p.notify(**data)
        rsp.raise_on_errors()
