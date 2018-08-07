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

    def test_email_from_key(self, provider):
        rsp = provider.notify(to='foo@foo.com', from_='bla@foo.com', message='foo', host='goo')
        rsp_data = rsp.data
        assert not rsp_data.get('from_')
        assert rsp_data['from'] == 'bla@foo.com'

    def test_multiple_to(self, provider):
        to = [
            'foo@foo.com',
            'bar@foo.com'
        ]
        rsp = provider.notify(to=to, message='foo', host='goo')
        assert rsp.data['to'] == ','.join(to)

    def test_gmail_negative(self, provider):
        data = {
            'username': 'foo',
            'password': 'foo',
            'to': 'foo@foo.com',
            'message': 'bar'
        }
        rsp = provider.notify(**data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert 'Username and Password not accepted' in e.value.errors[0]
