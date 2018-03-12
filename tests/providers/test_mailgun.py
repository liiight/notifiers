import pytest

from notifiers.exceptions import BadArguments

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
