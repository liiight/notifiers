import logging
import os
from datetime import datetime
from functools import partial
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from notifiers.core import get_notifier
from notifiers.core import SUCCESS_STATUS
from notifiers.logging import NotificationHandler
from notifiers.models.provider import Provider
from notifiers.models.provider import ProviderResource
from notifiers.models.response import Response
from notifiers.providers import _all_providers
from notifiers.utils.helpers import text_to_bool
from notifiers.utils.schema.helpers import list_to_commas
from notifiers.utils.schema.helpers import one_or_more

log = logging.getLogger(__name__)


class MockProxy:
    name = "mock_provider"


class MockResource(MockProxy, ProviderResource):
    resource_name = "mock_resource"

    _required = {"required": ["key"]}
    _schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "title": "required key"},
            "another_key": {"type": "integer", "title": "non-required key"},
        },
        "additionalProperties": False,
    }

    def _get_resource(self, data: dict):
        return {"status": SUCCESS_STATUS}


class MockProvider(MockProxy, Provider):
    """Mock Provider"""

    base_url = "https://api.mock.com"
    _required = {"required": ["required"]}
    _schema = {
        "type": "object",
        "properties": {
            "not_required": one_or_more(
                {"type": "string", "title": "example for not required arg"}
            ),
            "required": {"type": "string"},
            "option_with_default": {"type": "string"},
            "message": {"type": "string"},
        },
        "additionalProperties": False,
    }
    site_url = "https://www.mock.com"

    @property
    def defaults(self):
        return {"option_with_default": "foo"}

    def _send_notification(self, data: dict):
        return Response(status=SUCCESS_STATUS, provider=self.name, data=data)

    def _prepare_data(self, data: dict):
        if data.get("not_required"):
            data["not_required"] = list_to_commas(data["not_required"])
        data["required"] = list_to_commas(data["required"])
        return data

    @property
    def resources(self):
        return ["mock_rsrc"]

    @property
    def mock_rsrc(self):
        return MockResource()


@pytest.fixture(scope="session")
def mock_provider():
    """Return a generic :class:`notifiers.core.Provider` class"""
    _all_providers.update({MockProvider.name: MockProvider})
    return MockProvider()


@pytest.fixture
def bad_provider():
    """Returns an unimplemented :class:`notifiers.core.Provider` class for testing"""

    class BadProvider(Provider):
        pass

    return BadProvider


@pytest.fixture
def bad_schema():
    """Return a provider with an invalid JSON schema"""

    class BadSchema(Provider):
        _required = {"required": ["fpp"]}
        _schema = {"type": "banana"}

        name = "bad_schmea"
        base_url = ""
        site_url = ""

        def _send_notification(self, data: dict):
            pass

    return BadSchema


@pytest.fixture(scope="class")
def provider(request):
    name = getattr(request.module, "provider", None)
    if not name:
        pytest.fail(f"Test class '{request.module}' has not 'provider' attribute set")
    p = get_notifier(name)
    if not p:
        pytest.fail(f"No notifier with name '{name}'")
    return p


@pytest.fixture(scope="class")
def resource(request, provider):
    name = getattr(request.cls, "resource", None)
    if not name:
        pytest.fail(f"Test class '{request.cls}' has not 'resource' attribute set")
    resource = getattr(provider, name, None)
    if not resource:
        pytest.fail(f"Provider {provider.name} does not have a resource named {name}")
    return resource


@pytest.fixture
def cli_runner(monkeypatch):
    from notifiers_cli.core import notifiers_cli, provider_group_factory

    monkeypatch.setenv("LC_ALL", "en_US.utf-8")
    monkeypatch.setenv("LANG", "en_US.utf-8")
    provider_group_factory()
    runner = CliRunner()
    return partial(runner.invoke, notifiers_cli, obj={})


@pytest.fixture
def magic_mock_provider(monkeypatch):
    MockProvider.notify = MagicMock()
    MockProxy.name = "magic_mock"
    monkeypatch.setitem(_all_providers, MockProvider.name, MockProvider)
    return MockProvider()


@pytest.fixture
def handler(caplog):
    def return_handler(provider_name, logging_level, data=None, **kwargs):
        caplog.set_level(logging.INFO)
        hdlr = NotificationHandler(provider_name, data, **kwargs)
        hdlr.setLevel(logging_level)
        return hdlr

    return return_handler


def pytest_runtest_setup(item):
    """Skips PRs if secure env vars are set and test is marked as online"""
    pull_request = text_to_bool(os.environ.get("TRAVIS_PULL_REQUEST"))
    secure_env_vars = text_to_bool(os.environ.get("TRAVIS_SECURE_ENV_VARS"))
    online = item.get_closest_marker("online")
    if online and pull_request and not secure_env_vars:
        pytest.skip("skipping online tests via PRs")


@pytest.fixture
def test_message(request):
    message = os.environ.get("TRAVIS_BUILD_WEB_URL") or "Local test"
    return f"{message}-{request.node.name}-{datetime.now().isoformat()}"
