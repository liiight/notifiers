"""Checks that apply to every built in provider and its resources"""

import json
import re
import typing

import pytest
from pydantic import BaseModel

from notifiers.core import Provider, ProviderResource
from notifiers.exceptions import BadArguments
from notifiers.providers import _all_providers

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")


def _models(model: type[BaseModel]):
    """A model and every model nested in its fields"""
    yield model
    for field in model.model_fields.values():
        for arg in _flatten(field.annotation):
            if isinstance(arg, type) and issubclass(arg, BaseModel):
                yield from _models(arg)


def _flatten(annotation):
    yield annotation
    for arg in typing.get_args(annotation):
        yield from _flatten(arg)


def _resources():
    for name, cls in _all_providers.items():
        provider = cls()
        for resource_name in provider.resources:
            yield pytest.param(getattr(provider, resource_name), id=f"{name}-{resource_name}")


@pytest.mark.parametrize("provider_cls", _all_providers.values(), ids=_all_providers.keys())
class TestAllProviders:
    def test_is_provider(self, provider_cls):
        provider = provider_cls()
        assert isinstance(provider, Provider)
        assert set(provider.metadata) >= {"base_url", "site_url", "name"}

    def test_schema(self, provider_cls):
        provider = provider_cls()
        schema = provider.schema
        # schema, required and defaults are exposed via the CLI as JSON
        json.dumps(schema)
        json.dumps(provider.required)
        json.dumps(provider.defaults)
        assert schema["type"] == "object"
        assert provider.arguments == schema["properties"]
        assert set(provider.required["required"]) <= set(schema["properties"])
        assert set(provider.defaults) <= set(schema["properties"])

    def test_field_names_are_snake_case(self, provider_cls):
        """Python attributes are snake_case. Names used by the remote API (e.g. camelCase) belong in an alias"""
        for model in _models(provider_cls().schema_model):
            for name in model.model_fields:
                assert SNAKE_CASE.match(name), f"{model.__name__}.{name} is not snake_case, rename it and set the original name as its alias"

    def test_missing_required_raises_bad_arguments(self, provider_cls):
        with pytest.raises(BadArguments) as e:
            provider_cls().notify(env_prefix="notifiers_test_no_such_prefix_")
        assert e.value.errors


@pytest.mark.parametrize("resource", _resources())
def test_resources(resource):
    assert isinstance(resource, ProviderResource)
    json.dumps(resource.schema)
    json.dumps(resource.required)
    with pytest.raises(BadArguments):
        resource(env_prefix="notifiers_test_no_such_prefix_")
