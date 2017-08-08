import os

import pytest

from notifiers.core import NotificationProvider, NotificationResponse
from notifiers.utils.json_schema import one_or_more, list_to_commas


@pytest.fixture
def mock_provider() -> NotificationProvider:
    class MockProvider(NotificationProvider):
        base_url = 'https://api.mock.com'
        schema = {
            'type': 'object',
            'properties': {
                'not_required': one_or_more({'type': 'string'}),
                'required': {'type': 'string'}
            },
            'required': ['required'],
            'additionalProperties': False
        }
        site_url = 'https://www.mock.com'
        provider_name = 'mock_provider'

        def _send_notification(self, data: dict):
            return NotificationResponse(status='success', provider=self.provider_name, data=data)

        def _prepare_data(self, data: dict):
            if data.get('not_required'):
                data['not_required'] = list_to_commas(data['not_required'])
            data['required'] = list_to_commas(data['required'])
            return data

    from notifiers.providers import _all_providers
    _all_providers['mock'] = MockProvider
    return MockProvider


@pytest.fixture
def bad_provider() -> NotificationProvider:
    class BadProvider(NotificationProvider):
        pass

    return BadProvider


@pytest.fixture
def set_environs():
    def wrapper_set_environs(**kwargs):
        for key, value in kwargs.items():
            os.environ[key] = value

    return wrapper_set_environs
