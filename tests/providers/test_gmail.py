import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestGmail(object):
    """Gmail tests"""

    def test_gmail_metadata(self):
        p = get_notifier('gmail')
        assert p.metadata == {
            'base_url': 'smtp.gmail.com',
            'provider_name': 'gmail',
            'site_url': 'https://www.google.com/gmail/about/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'to')
    ])
    def test_gmail_missing_required(self, data, message):
        p = get_notifier('gmail')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_smtp_sanity(self):
        """using Gmail SMTP"""
        data = {
            'message': '<b>foo</b>',
            'html': True
        }
        p = get_notifier('gmail')
        rsp = p.notify(**data)
        rsp.raise_on_errors()
