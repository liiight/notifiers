import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments


class TestPushover(object):
    """Pushover notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_PUSHOVER_TOKEN and NOTIFIERS_PUSHOVER_USER
    """

    def test_missing_required(self):
        p = get_notifier('pushover')
        with pytest.raises(BadArguments) as e:
            p.notify(env_prefix='test')
        assert '\'user\' is a required property' in e.value.message

        with pytest.raises(BadArguments) as e:
            p.notify(user='foo', env_prefix='test')
        assert '\'message\' is a required property' in e.value.message

        with pytest.raises(BadArguments) as e:
            p.notify(message='bla', user='foo', env_prefix='test')
        assert '\'token\' is a required property' in e.value.message

    def test_pushover_restrictions(self):
        """Pushover specific API restrictions:

        Priority value 2
        """

    def test_sanity(self):
        """Successful pushover notification"""

    def test_all_options(self):
        """Use all available pushover options"""
