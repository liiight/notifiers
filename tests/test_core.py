import sys
import typing

import pytest

import notifiers
from notifiers import notify
from notifiers.core import SUCCESS_STATUS, Provider, Response
from notifiers.exceptions import (
    BadArguments,
    NoSuchNotifierError,
    NotificationError,
)


class TestCore:
    """Test core classes"""

    valid_data: typing.ClassVar = {"required": "foo", "not_required": ["foo", "bar"]}

    def test_sanity(self, mock_provider):
        """Test basic notification flow"""
        assert mock_provider.metadata == {
            "base_url": "https://api.mock.com",
            "name": "mock_provider",
            "site_url": "https://www.mock.com",
        }
        assert mock_provider.schema == mock_provider.schema_model.model_json_schema(by_alias=True)
        assert mock_provider.arguments == mock_provider.schema["properties"]
        assert list(mock_provider.arguments) == ["not_required", "required", "option_with_default", "message"]
        assert mock_provider.defaults == {"option_with_default": "foo"}

        assert mock_provider.required == {"required": ["required"]}
        rsp = mock_provider.notify(**self.valid_data)
        assert isinstance(rsp, Response)
        assert not rsp.errors
        assert rsp.raise_on_errors() is None
        assert repr(rsp) == f"<Response,provider=Mock_provider,status={SUCCESS_STATUS}, errors=None>"
        assert repr(mock_provider) == "<Provider:[Mock_provider]>"

    @pytest.mark.parametrize(
        ("data", "message"),
        [
            pytest.param({"not_required": "foo"}, "'required' is a required property", id="Missing required"),
            pytest.param({"required": ["foo"]}, "'required': Input should be a valid string", id="Wrong type"),
            pytest.param({"required": "foo", "foo": 6}, "Additional properties are not allowed ('foo' was unexpected)", id="Additional properties not allowed"),
            pytest.param({"required": "foo", "not_required": []}, "'not_required': List should have at least 1 item", id="Empty list"),
            pytest.param({"required": "foo", "not_required": ["a", "a"]}, "has non-unique elements", id="Non unique items"),
        ],
    )
    def test_schema_validation(self, data, message, mock_provider):
        """Test correct schema validations"""
        with pytest.raises(BadArguments) as e:
            mock_provider.notify(**data)
        assert message in e.value.message
        assert e.value.errors
        assert all({"loc", "msg", "type"} <= set(error) for error in e.value.errors)

    def test_schema_validation_coerces_types(self, mock_provider):
        """Values are coerced to their declared type (lax mode), e.g. strings from environment variables"""
        resource = mock_provider.mock_rsrc
        assert resource._process_data(key="foo", another_key="5") == {"key": "foo", "another_key": 5}

    def test_environs_are_coerced(self, mock_provider, monkeypatch):
        """Environment variables (always strings) are coerced to the declared type"""
        resource = mock_provider.mock_rsrc
        monkeypatch.setenv("NOTIFIERS_MOCK_PROVIDER_ANOTHER_KEY", "7")
        assert resource._process_data(key="foo") == {"key": "foo", "another_key": 7}

    def test_prepare_data(self, mock_provider):
        """Test ``prepare_data()`` method"""
        rsp = mock_provider.notify(**self.valid_data)
        assert rsp.data == {
            "not_required": "foo,bar",
            "required": "foo",
            "option_with_default": "foo",
        }

    def test_get_notifier(self, mock_provider):
        """Test ``get_notifier()`` helper function"""
        p = notifiers.get_notifier("mock_provider")
        assert p
        assert isinstance(p, Provider)

    def test_all_providers(self, mock_provider, monkeypatch):
        """Test ``all_providers()`` helper function"""

        def mock_providers():
            return ["mock"]

        monkeypatch.setattr(notifiers, "all_providers", mock_providers)

        assert "mock" in notifiers.all_providers()

    def test_error_response(self, mock_provider):
        """Test error notification response"""
        rsp = mock_provider.notify(**self.valid_data)
        rsp.errors = ["an error"]
        rsp.status = "fail"

        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert repr(e.value) == "<NotificationError: Notification errors: an error>"
        assert e.value.errors == ["an error"]
        assert e.value.data == {
            "not_required": "foo,bar",
            "required": "foo",
            "option_with_default": "foo",
        }
        assert e.value.message == "Notification errors: an error"
        assert e.value.provider == mock_provider.name

    def test_bad_integration(self, bad_provider):
        """Test bad provider inheritance"""
        with pytest.raises(TypeError) as e:
            bad_provider()
        if sys.version_info < (3, 12):
            assert ("Can't instantiate abstract class BadProvider with abstract methods _send_notification, base_url, name, schema_model, site_url") in str(e.value)
        else:
            assert (
                "Can't instantiate abstract class BadProvider without an implementation for abstract methods "
                "'_send_notification', 'base_url', 'name', 'schema_model', 'site_url'" in str(e.value)
            )

    def test_environs(self, mock_provider, monkeypatch):
        """Test environs usage"""
        prefix = "mock_"
        monkeypatch.setenv(f"{prefix}{mock_provider.name}_required".upper(), "foo")
        rsp = mock_provider.notify(env_prefix=prefix)
        assert rsp.status == SUCCESS_STATUS
        assert rsp.data["required"] == "foo"

    def test_provided_data_takes_precedence_over_environ(self, mock_provider, monkeypatch):
        """Verify that given data overrides environ"""
        prefix = "mock_"
        monkeypatch.setenv(f"{prefix}{mock_provider.name}_required".upper(), "foo")
        rsp = mock_provider.notify(required="bar", env_prefix=prefix)
        assert rsp.status == SUCCESS_STATUS
        assert rsp.data["required"] == "bar"

    def test_resources(self, mock_provider):
        resources = getattr(mock_provider, "resources", None)
        assert resources is not None
        assert isinstance(resources, list)
        assert "mock_rsrc" in resources

        rsrc = resources[0]
        resource = getattr(mock_provider, rsrc)
        assert resource
        assert repr(resource) == "<ProviderResource,provider=mock_provider,resource=mock_resource>"
        assert resource.resource_name == "mock_resource"
        assert resource.name == mock_provider.name
        assert resource.schema == resource.schema_model.model_json_schema(by_alias=True)
        assert resource.arguments["key"]["description"] == "required key"

        assert resource.required == {"required": ["key"]}

        with pytest.raises(BadArguments):
            resource()

        rsp = resource(key="fpp")
        assert rsp == {"status": SUCCESS_STATUS}

    def test_direct_notify_positive(self, mock_provider):
        rsp = notify(mock_provider.name, required="foo", message="foo")
        assert not rsp.errors
        assert rsp.status == SUCCESS_STATUS
        assert rsp.data == {
            "required": "foo",
            "message": "foo",
            "option_with_default": "foo",
        }

    def test_direct_notify_negative(self):
        with pytest.raises(NoSuchNotifierError, match="No such notifier with name"):
            notify("foo", message="whateverz")


class TestEntryPointProviders:
    """Providers registered by installed packages via the ``notifiers`` entry point group"""

    @pytest.fixture
    def plugin_dist(self, tmp_path, monkeypatch):
        """A fake installed distribution exposing ``plugin_provider`` in the ``notifiers`` group"""
        (tmp_path / "notifiers_test_plugin.py").write_text("from conftest import MockProvider\n\nclass PluginProvider(MockProvider):\n    name = 'plugin_provider'\n")
        dist_info = tmp_path / "notifiers_test_plugin-1.0.dist-info"
        dist_info.mkdir()
        (dist_info / "METADATA").write_text("Metadata-Version: 2.1\nName: notifiers-test-plugin\nVersion: 1.0\n")
        (dist_info / "entry_points.txt").write_text("[notifiers]\nplugin_provider = notifiers_test_plugin:PluginProvider\n")
        monkeypatch.syspath_prepend(str(tmp_path))
        return tmp_path

    def test_entry_point_provider_is_discovered(self, plugin_dist):
        assert "plugin_provider" in notifiers.all_providers()
        provider = notifiers.get_notifier("plugin_provider", strict=True)
        assert provider.name == "plugin_provider"
        assert provider.notify(required="foo").ok
