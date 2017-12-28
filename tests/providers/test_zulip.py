import pytest

import datetime

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestZulip:
    notifier_name = 'zulip'

    def test_metadata(self):
        p = get_notifier(self.notifier_name)
        assert p.metadata == {
            'base_url': 'https://{domain}.zulipchat.com',
            'site_url': 'https://zulipchat.com/api/',
            'provider_name': 'zulip'
        }

    @pytest.mark.parametrize('data, message', [
        ({'email': 'foo', 'api_key': 'bar', 'message': 'boo', 'to': 'bla'}, 'domain'),
        ({'email': 'foo', 'api_key': 'bar', 'message': 'boo', 'to': 'bla', 'domain': 'bla', 'server': 'fop'},
         "Only one of 'domain' or 'server' is allowed"),
    ])
    def test_missing_required(self, data, message):
        p = get_notifier(self.notifier_name)
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert message in e.value.message

    @pytest.mark.online
    def test_sanity(self):
        p = get_notifier(self.notifier_name)
        data = {
            'to': 'general',
            'message': str(datetime.datetime.now()),
            'domain': 'notifiers',
            'subject': 'test'
        }
        rsp = p.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_private_message(self):
        p = get_notifier(self.notifier_name)
        data = {
            'message': str(datetime.datetime.now()),
            'domain': 'notifiers',
            'type': 'private'
        }
        rsp = p.notify(**data)
        rsp.raise_on_errors()
