import pytest

from notifiers.core import Provider, Response
from notifiers.providers import _all_providers
from notifiers.utils.json_schema import one_or_more, list_to_commas


@pytest.fixture
def mock_provider(monkeypatch) -> Provider:
    """Return a generic :class:``notifiers.Provider`` class"""

    class MockProvider(Provider):
        base_url = 'https://api.mock.com'
        schema = {
            'type': 'object',
            'properties': {
                'not_required': one_or_more({'type': 'string'}),
                'required': {'type': 'string'},
                'option_with_default': {'type': 'string'},
                'message': {'type': 'string'}
            },
            'required': ['required'],
            'additionalProperties': False
        }
        site_url = 'https://www.mock.com'
        provider_name = 'mock_provider'

        @property
        def defaults(self):
            return {
                'option_with_default': 'foo'
            }

        def _send_notification(self, data: dict):
            return Response(status='success', provider=self.provider_name, data=data)

        def _prepare_data(self, data: dict):
            if data.get('not_required'):
                data['not_required'] = list_to_commas(data['not_required'])
            data['required'] = list_to_commas(data['required'])
            return data

    monkeypatch.setitem(_all_providers, 'mock', MockProvider)
    return MockProvider


@pytest.fixture
def bad_provider() -> Provider:
    """Returns an unimplemented :class:``notifiers.Provider`` class for testing"""

    class BadProvider(Provider):
        pass

    return BadProvider
