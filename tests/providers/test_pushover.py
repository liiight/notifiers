import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments


class TestPushover(object):
    """Pushover notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_PUSHOVER_TOKEN and NOTIFIERS_PUSHOVER_USER
    """

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
        assert f'\'{message}\' is a required property' in e.value.message

    def test_pushover_restrictions(self):
        """Pushover specific API restrictions:

        Priority value 2
        """

    def test_sanity(self):
        """Successful pushover notification"""
        p = get_notifier('pushover')
        data = {'message': 'foo'}
        rsp = p.notify(**data)
        rsp.raise_on_errors()

    def test_all_options(self):
        """Use all available pushover options"""
