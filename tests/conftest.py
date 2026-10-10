import logging
import os
from datetime import datetime
from functools import partial
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pydantic import Field

from notifiers.core import (
    SUCCESS_STATUS,
    Provider,
    ProviderResource,
    Response,
    get_notifier,
)
from notifiers.logging import NotificationHandler
from notifiers.models import OneOrMore, SchemaModel
from notifiers.providers import _all_providers
from notifiers.utils.helpers import list_to_commas, text_to_bool
from notifiers_cli.core import notifiers_cli

log = logging.getLogger(__name__)


class MockProxy:
    name = "mock_provider"


class MockResourceSchema(SchemaModel):
    key: str = Field(description="required key")
    another_key: int | None = Field(None, description="non-required key")


class MockResource(MockProxy, ProviderResource):
    resource_name = "mock_resource"

    schema_model = MockResourceSchema

    def _get_resource(self, data: dict):
        return {"status": SUCCESS_STATUS}


class MockProviderSchema(SchemaModel):
    not_required: OneOrMore[str] | None = Field(None, description="example for not required arg")
    required: str
    option_with_default: str = "foo"
    message: str | None = None


class MockProvider(MockProxy, Provider):
    """Mock Provider"""

    base_url = "https://api.mock.com"
    schema_model = MockProviderSchema
    site_url = "https://www.mock.com"

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
    monkeypatch.setenv("LC_ALL", "en_US.utf-8")
    monkeypatch.setenv("LANG", "en_US.utf-8")
    runner = CliRunner()
    return partial(runner.invoke, notifiers_cli, obj={})


@pytest.fixture
def magic_mock_provider(monkeypatch):
    # monkeypatch restores the class attributes after the test, so other tests see the real MockProvider
    monkeypatch.setattr(MockProvider, "notify", MagicMock())
    monkeypatch.setattr(MockProxy, "name", "magic_mock")
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


@pytest.fixture(autouse=True)
def isolate_offline_tests_from_credentials(request, monkeypatch):
    """Offline tests must not depend on provider credentials (``NOTIFIERS_*``) set for online tests, e.g. in CI"""
    if request.node.get_closest_marker("online"):
        return
    for key in list(os.environ):
        if key.startswith("NOTIFIERS_"):
            monkeypatch.delenv(key)


def pytest_addoption(parser):
    parser.addoption(
        "--run-skipped-online",
        action="store_true",
        default=text_to_bool(os.environ.get("NOTIFIERS_RUN_SKIPPED_ONLINE")),
        help="Run online tests even if they're marked as skipped, e.g. to check whether a disabled account works again. Can also be enabled with NOTIFIERS_RUN_SKIPPED_ONLINE=1",
    )


def pytest_collection_modifyitems(config, items):
    """With ``--run-skipped-online``, ``skip`` markers on online tests are ignored"""
    if not config.getoption("--run-skipped-online"):
        return
    for item in items:
        if not item.get_closest_marker("online"):
            continue
        skips = list(item.iter_markers("skip"))
        if skips:
            reasons = "; ".join(m.kwargs.get("reason") or (m.args[0] if m.args else "") for m in skips)
            item.user_properties.append(("ignored_skip", reasons))
            item.own_markers = [m for m in item.own_markers if m.name != "skip"]
            for node in item.listchain():
                node.own_markers = [m for m in node.own_markers if m.name != "skip"]


def pytest_runtest_setup(item):
    """Online tests need provider credentials. On pull requests from forks GitHub doesn't expose secrets, so skip them"""
    if not item.get_closest_marker("online"):
        return
    if os.environ.get("GITHUB_ACTIONS") and not any(key.startswith("NOTIFIERS_") and value for key, value in os.environ.items()):
        pytest.skip("online tests need NOTIFIERS_* secrets, which aren't available")


@pytest.fixture
def test_message(request):
    message = "Local test"
    if os.environ.get("GITHUB_RUN_ID"):
        message = f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    return f"{message}-{request.node.name}-{datetime.now().isoformat()}"
