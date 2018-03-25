import datetime

import pytest

from notifiers.core import FAILURE_STATUS
from notifiers.exceptions import BadArguments, ResourceError

provider = 'statuspage'


class TestStatusPage:

    def test_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://api.statuspage.io/v1//pages/{page_id}/',
            'name': 'statuspage',
            'site_url': 'https://statuspage.io'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'api_key'),
        ({'message': 'foo', 'api_key': 1}, 'page_id')
    ])
    def test_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments, match=f"'{message}' is a required property"):
            provider.notify(**data)

    @pytest.mark.parametrize('added_data, message', [
        ({
             'scheduled_for': 'foo',
             'scheduled_until': 'foo',
             'backfill_date': 'foo',
             'backfilled': True
         }, "Cannot set both 'backfill' and 'scheduled' incident properties in the same notification!"),
        ({
             'scheduled_for': 'foo',
             'scheduled_until': 'foo',
             'status': 'investigating'
         }, "is a realtime incident status! Please choose one of"),
        ({
             'backfill_date': 'foo',
             'backfilled': True,
             'status': 'investigating'
         }, "Cannot set 'status' when setting 'backfill'!")
    ])
    def test_data_dependencies(self, added_data, message, provider):
        data = {
            'api_key': 'foo',
            'message': 'foo',
            'page_id': 'foo'
        }
        data.update(added_data)
        with pytest.raises(BadArguments, match=message):
            provider.notify(**data)

    def test_errors(self, provider):
        data = {
            'api_key': 'foo',
            'page_id': 'foo',
            'message': 'foo'
        }
        rsp = provider.notify(**data)
        assert rsp.status == FAILURE_STATUS
        assert 'Could not authenticate' in rsp.errors

    @pytest.mark.online
    @pytest.mark.parametrize('data', [
        ({
            'message': 'foo'
        }),
        ({
            'message': 'Test realitme',
            'status': 'investigating',
            'body': 'Incident body',
            'wants_twitter_update': False,
            'impact_override': 'minor',
            'deliver_notifications': False,
        }),
        ({
            'message': 'Test scheduled',
            'status': 'scheduled',
            'body': 'Incident body',
            'wants_twitter_update': False,
            'impact_override': 'minor',
            'deliver_notifications': False,
            'scheduled_for': (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).isoformat(),
            'scheduled_until': (datetime.datetime.utcnow() + datetime.timedelta(minutes=2)).isoformat(),
            'scheduled_remind_prior': False,
            'scheduled_auto_in_progress': True,
            'scheduled_auto_completed': True
        }),
        ({
            'message': 'Test backfill',
            'body': 'Incident body',
            'impact_override': 'minor',
            'backfilled': True,
            'backfill_date': (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        })
    ])
    def test_success(self, data, provider):
        provider.notify(**data, raise_on_errors=True)


class TestStatuspageComponents:
    resource = 'components'

    def test_statuspage_components_attribs(self, resource):
        assert resource.schema == {
            'additionalProperties': False,
            'properties': {'api_key': {'title': 'OAuth2 token', 'type': 'string'},
                           'page_id': {'title': 'Page ID', 'type': 'string'}},
            'required': ['api_key', 'page_id'],
            'type': 'object'
        }

        assert resource.name == provider
        assert resource.required == {'required': ['api_key', 'page_id']}

    def test_statuspage_components_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix='foo')

        with pytest.raises(ResourceError, match='Could not authenticate'):
            resource(api_key='foo', page_id='bar')
