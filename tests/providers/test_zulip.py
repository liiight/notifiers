import datetime

import pytest

from notifiers.exceptions import BadArguments, NotifierException

provider = 'zulip'


class TestZulip:

    def test_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://{domain}.zulipchat.com',
            'site_url': 'https://zulipchat.com/api/',
            'name': 'zulip'
        }

    @pytest.mark.parametrize('data, message', [
        ({'email': 'foo', 'api_key': 'bar', 'message': 'boo', 'to': 'bla'}, 'domain'),
        ({'email': 'foo', 'api_key': 'bar', 'message': 'boo', 'to': 'bla', 'domain': 'bla', 'server': 'fop'},
         "Only one of 'domain' or 'server' is allowed"),
    ])
    def test_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert message in e.value.message

    @pytest.mark.online
    def test_sanity(self, provider):
        data = {
            'to': 'general',
            'message': str(datetime.datetime.now()),
            'domain': 'notifiers',
            'subject': 'test'
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_private_message(self, provider):
        data = {
            'message': str(datetime.datetime.now()),
            'domain': 'notifiers',
            'type': 'private'
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_zulip_type_key(self, provider):
        rsp = provider.notify(email='foo', api_key='bar', to='baz', domain='bla', type_='private', message='foo')
        rsp_data = rsp.data
        assert not rsp_data.get('type_')
        assert rsp_data['type'] == 'private'

    def test_zulip_missing_subject(self, provider):
        with pytest.raises(NotifierException) as e:
            provider.notify(email='foo', api_key='bar', to='baz', domain='bla', type_='stream', message='foo')
        assert "'subject' is required when 'type' is 'stream'" in e.value.message
