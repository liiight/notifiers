import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestSMTP(object):
    """SMTP tests"""

    def test_smtp_metadata(self):
        p = get_notifier('email')
        assert p.metadata == {
            'base_url': None,
            'provider_name': 'email',
            'site_url': 'https://en.wikipedia.org/wiki/Email'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'to')
    ])
    def test_smtp_missing_required(self, data, message):
        p = get_notifier('email')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f'\'{message}\' is a required property' in e.value.message

    def test_smtp_no_host(self):
        p = get_notifier('email')
        data = {
            'to': 'foo',
            'message': 'bar',
            'host': 'http://nohost'
        }
        with pytest.raises(NotificationError) as e:
            rsp = p.notify(**data)
            rsp.raise_on_errors()
        possible_errors = ['Errno 111', 'Errno 61', 'Errno 8', 'Errno -2']
        assert any(error in e.value.message for error in possible_errors), \
            f'Error not in expected errors; {e.value.message}'
        assert any(error in rsp_error for rsp_error in rsp.errors for error in possible_errors), \
            f'Error not in expected errors; {rsp.errors}'

    @pytest.mark.online
    def test_smtp_sanity(self):
        """using Gmail SMTP"""
        data = {
            'message': '<b>foo</b>',
            'host': 'smtp.gmail.com',
            'port': 587,
            'tls': True,
            'html': True
        }
        p = get_notifier('email')
        rsp = p.notify(**data)
        rsp.raise_on_errors()
