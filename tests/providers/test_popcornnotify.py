import pytest

from notifiers.core import FAILURE_STATUS
from notifiers.exceptions import BadArguments, NotificationError

provider = 'popcornnotify'


class TestPopcornNotify:

    def test_popcornnotify_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://popcornnotify.com/notify',
            'name': 'popcornnotify',
            'site_url': 'https://popcornnotify.com/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'api_key'),
        ({'message': 'foo', 'api_key': 'foo'}, 'recipients'),
    ])
    def test_popcornnotify_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_popcornnotify_sanity(self, provider):
        data = {
            'message': 'foo'
        }
        provider.notify(**data, raise_on_errors=True)

    def test_popcornnotify_error(self, provider):
        data = {
            'message': 'foo',
            'api_key': 'foo',
            'recipients': 'foo@foo.com'
        }
        rsp = provider.notify(**data)
        assert rsp.status == FAILURE_STATUS
        error = 'Please provide a valid API key'
        assert error in rsp.errors
        with pytest.raises(NotificationError, match=error):
            rsp.raise_on_errors()
