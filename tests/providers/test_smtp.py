import pytest

from notifiers.exceptions import BadArguments, NotificationError

provider = 'email'


class TestSMTP(object):
    """SMTP tests"""

    def test_smtp_metadata(self, provider):
        assert provider.metadata == {
            'base_url': None,
            'name': 'email',
            'site_url': 'https://en.wikipedia.org/wiki/Email'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'to')
    ])
    def test_smtp_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    def test_smtp_no_host(self, provider):
        data = {
            'to': 'foo',
            'message': 'bar',
            'host': 'http://nohost'
        }
        with pytest.raises(NotificationError) as e:
            rsp = provider.notify(**data)
            rsp.raise_on_errors()
        possible_errors = ['Errno 111', 'Errno 61', 'Errno 8', 'Errno -2']
        assert any(error in e.value.message for error in possible_errors), \
            f'Error not in expected errors; {e.value.message}'
        assert any(error in rsp_error for rsp_error in rsp.errors for error in possible_errors), \
            f'Error not in expected errors; {rsp.errors}'

    def test_email_from_key(self, provider):
        rsp = provider.notify(to='foo', from_='bla', message='foo')
        rsp_data = rsp.data
        assert not rsp_data.get('from_')
        assert rsp_data['from'] == 'bla'

    def test_multiple_to(self, provider):
        to = ['foo', 'bar']
        rsp = provider.notify(to=to, message='foo')
        assert rsp.data['to'] == ','.join(to)

    def test_attachment(self, provider, tmpdir):
        dir_ = tmpdir.mkdir('sub')
        file_1 = dir_.join('foo.txt')
        file_2 = dir._join('bar.txt')
        file_3 = dir._join('baz.txt')
        attachments = [file_1, file_2, file_3]
        rsp = provider.notify(to='foo', message='bar', attachments=attachments)
        assert rsp.data['attachments'] == attachments

    @pytest.mark.online
    def test_smtp_sanity(self, provider):
        """using Gmail SMTP"""
        data = {
            'message': '<b>foo</b>',
            'host': 'smtp.gmail.com',
            'port': 587,
            'tls': True,
            'html': True
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()
