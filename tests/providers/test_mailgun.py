import pytest
import datetime
import time
from email import utils
from notifiers.exceptions import BadArguments
from notifiers.core import FAILURE_STATUS

provider = 'mailgun'


class TestMailgun:

    def test_mailgun_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://api.mailgun.net/v3/{domain}/messages',
            'name': 'mailgun',
            'site_url': 'https://documentation.mailgun.com/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'to'),
        ({'to': 'foo'}, 'domain'),
        ({'to': 'foo', 'domain': 'bla'}, 'api_key'),
        ({'to': 'foo', 'domain': 'bla', 'api_key': 'bla'}, 'from'),
        ({'to': 'foo', 'domain': 'bla', 'api_key': 'bla', 'from': 'bbb'}, 'message')
    ])
    def test_mailgun_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments, match=f"'{message}' is a required property"):
            provider.notify(**data)

    @pytest.mark.online
    def test_mailgun_sanity(self, provider):
        provider.notify(message='foo', raise_on_errors=True)

    @pytest.mark.online
    def test_mailgun_all_options(self, provider, tmpdir):
        dir_ = tmpdir.mkdir("sub")
        file_1 = dir_.join("hello.txt")
        file_1.write("content")

        file_2 = dir_.join("world.txt")
        file_2.write("content")

        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        rfc_2822 = utils.formatdate(time.mktime(now.timetuple()))
        data = {
            'message': 'foo',
            'html': f'<b>{now}</b>',
            'subject': f'{now}',
            'attachment': [
                file_1.strpath,
                file_2.strpath
            ],
            'inline': [
                file_1.strpath,
                file_2.strpath
            ],
            'tag': [
                'foo',
                'bar'
            ],
            'dkim': True,
            'deliverytime': rfc_2822,
            'testmode': False,
            'tracking': True,
            'tracking_clicks': True,
            'tracking_opens': True,
            'require_tls': False,
            'skip_verification': True,
            'headers': {
                'foo': 'bar'
            },
            'data': {
                'foo': {
                    'bar': 'bla'
                }
            }
        }
        provider.notify(**data, raise_on_errors=True)

    def test_mailgun_error_response(self, provider):
        data = {
            'api_key': 'FOO',
            'message': 'bla',
        }
        rsp = provider.notify(**data)
        assert rsp.status == FAILURE_STATUS
        assert 'Forbidden' in rsp.errors
