import logging
import os

import pytest

from notifiers.core import Provider, Response
from notifiers.providers import _all_providers
from notifiers.utils.helpers import text_to_bool
from notifiers.utils.json_schema import one_or_more, list_to_commas

log = logging.getLogger(__name__)


@pytest.fixture
def mock_provider(monkeypatch):
    """Return a generic :class:`notifiers.Provider` class"""

    class MockProvider(Provider):
        """Mock Provider"""
        base_url = 'https://api.mock.com'
        _required = {'required': ['required']}
        _schema = {
            'type': 'object',
            'properties': {
                'not_required': one_or_more({
                    'type': 'string',
                    'title': 'example for not required arg'
                }),
                'required': {'type': 'string'},
                'option_with_default': {'type': 'string'},
                'message': {'type': 'string'}
            },
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


@pytest.fixture(scope='session')
def load_cli_providers():
    from notifiers_cli.core import provider_group_factory
    provider_group_factory()


@pytest.fixture(scope='session')
def notifiers_cli_main():
    from notifiers_cli.core import notifiers_cli
    return notifiers_cli


def pytest_runtest_setup(item):
    """
    Skips PRs if secure env vars are set and test is marked as online
    """
    pull_request = text_to_bool(os.environ.get('TRAVIS_PULL_REQUEST'))
    secure_env_vars = text_to_bool(os.environ.get('TRAVIS_SECURE_ENV_VARS'))
    online = item.get_marker('online') is not None
    if online and pull_request and not secure_env_vars:
        pytest.skip('skipping online tests via PRs')
