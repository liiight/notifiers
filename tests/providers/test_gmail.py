import pytest

from notifiers.exceptions import BadArguments, NotificationError

provider = 'gmail'


class TestGmail:
    """Gmail tests"""

    def test_gmail_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'smtp.gmail.com',
            'name': 'gmail',
            'site_url': 'https://www.google.com/gmail/about/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'to')
    ])
    def test_gmail_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_smtp_sanity(self, provider):
        """using Gmail SMTP"""
        data = {
            'message': '<b>foo</b>',
            'html': True
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_gmail_negative(self, provider):
        data = {
            'username': 'foo',
            'password': 'foo',
            'to': 'foo',
            'message': 'bar'
        }
        rsp = provider.notify(**data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert e.value.errors == [b"(535, b\\'5.7.8 Username and Password not accepted. Learn more at\\n5.7.8 "
                                  b" https://support.google.com/mail/?p=BadCredentials h194sm13693945wma.8 - gsmtp\\')"]
