import logging
import os
from datetime import datetime
from functools import partial
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pydantic import Field
from pydantic import StrictStr
from pydantic import validator

from notifiers.core import get_notifier
from notifiers.logging import NotificationHandler
from notifiers.models.resource import Provider
from notifiers.models.resource import ProviderResource
from notifiers.models.response import Response
from notifiers.models.response import ResponseStatus
from notifiers.models.schema import ResourceSchema
from notifiers.providers import _all_providers
from notifiers.utils.helpers import text_to_bool

log = logging.getLogger(__name__)


class MockProxy:
    name = "mock_provider"


class MockResourceSchema(ResourceSchema):
    key: str = Field(..., description="required key")
    another_key: int = Field(None, description="non-required key")


class MockProviderSchema(ResourceSchema):
    not_required: ResourceSchema.one_or_more_of(str) = Field(
        None, description="example for not required arg"
    )
    required: StrictStr
    option_with_default = "foo"
    message: str = None

    @validator("not_required", whole=True)
    def csv(cls, v):
        return cls.to_comma_separated(v)


class MockResource(MockProxy, ProviderResource):
    resource_name = "mock_resource"

    schema_model = MockResourceSchema

    def _get_resource(self, data: dict):
        return {"status": ResponseStatus.SUCCESS}


class MockProvider(MockProxy, Provider):
    """Mock Provider"""

    base_url = "https://api.mock.com"
    site_url = "https://www.mock.com"
    schema_model = MockProviderSchema

    def _send_notification(self, data: MockProviderSchema):
        return Response(
            status=ResponseStatus.SUCCESS, provider=self.name, data=data.to_dict()
        )

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
