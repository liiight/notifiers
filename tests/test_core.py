import pytest

import notifiers
from notifiers import notify
from notifiers.exceptions import BadArguments
from notifiers.exceptions import NoSuchNotifierError
from notifiers.exceptions import NotificationError
from notifiers.models.provider import Provider
from notifiers.models.response import Response
from notifiers.models.response import ResponseStatus


class TestCore:
    """Test core classes"""

    valid_data = {"required": "foo", "not_required": ["foo", "bar"]}

    def test_sanity(self, mock_provider):
        """Test basic notification flow"""
        assert mock_provider.metadata == {
            "base_url": "https://api.mock.com",
            "name": "mock_provider",
            "site_url": "https://www.mock.com",
        }
        assert mock_provider.arguments == {
            "not_required": {
                "oneOf": [
                    {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "title": "example for not required arg",
                        },
                        "minItems": 1,
                        "uniqueItems": True,
                    },
                    {"type": "string", "title": "example for not required arg"},
                ]
            },
            "required": {"type": "string"},
            "option_with_default": {"type": "string"},
            "message": {"type": "string"},
        }

        assert mock_provider.required == {"required": ["required"]}
        rsp = mock_provider.notify(**self.valid_data)
        assert isinstance(rsp, Response)
        assert not rsp.errors
        assert rsp.raise_on_errors() is None
        assert (
            repr(rsp)
            == f"<Response,provider=Mock_provider,status={ResponseStatus.SUCCESS}, errors=None>"
        )
        assert repr(mock_provider) == "<Provider:[Mock_provider]>"

    @pytest.mark.parametrize(
        "data",
        [
            pytest.param({"not_required": "foo"}, id="Missing required"),
            pytest.param({"required": 6}, id="Wrong type"),
            pytest.param({"foo": 6}, id="Additional properties not allowed"),
        ],
    )
    def test_schema_validation(self, data, mock_provider):
        """Test correct schema validations"""
        with pytest.raises(BadArguments):
            mock_provider.notify(**data)

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
        from notifiers import get_notifier

        p = get_notifier("mock_provider")
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
        assert (
            "Can't instantiate abstract class BadProvider with abstract methods _required,"
            " _schema, _send_notification, base_url, name, site_url"
        ) in str(e.value)

    def test_environs(self, mock_provider, monkeypatch):
        """Test environs usage"""
        prefix = f"mock_"
        monkeypatch.setenv(f"{prefix}{mock_provider.name}_required".upper(), "foo")
        rsp = mock_provider.notify(env_prefix=prefix)
        assert rsp.status is ResponseStatus.SUCCESS
        assert rsp.data["required"] == "foo"

    def test_provided_data_takes_precedence_over_environ(
        self, mock_provider, monkeypatch
    ):
        """Verify that given data overrides environ"""
        prefix = f"mock_"
        monkeypatch.setenv(f"{prefix}{mock_provider.name}_required".upper(), "foo")
        rsp = mock_provider.notify(required="bar", env_prefix=prefix)
        assert rsp.status is ResponseStatus.SUCCESS
        assert rsp.data["required"] == "bar"

    def test_resources(self, mock_provider):
        resources = getattr(mock_provider, "resources", None)
        assert resources is not None
        assert isinstance(resources, list)
        assert "mock_rsrc" in resources

        rsrc = resources[0]
        resource = getattr(mock_provider, rsrc)
        assert resource
        assert (
            repr(resource)
            == "<ProviderResource,provider=mock_provider,resource=mock_resource>"
        )
        assert resource.resource_name == "mock_resource"
        assert resource.name == mock_provider.name
        assert resource.schema == {
            "type": "object",
            "properties": {
                "key": {"type": "string", "title": "required key"},
                "another_key": {"type": "integer", "title": "non-required key"},
            },
            "required": ["key"],
            "additionalProperties": False,
        }

        assert resource.required == {"required": ["key"]}

        with pytest.raises(BadArguments):
            resource()

        rsp = resource(key="fpp")
        assert rsp == {"status": ResponseStatus.SUCCESS}

    def test_direct_notify_positive(self, mock_provider):
        rsp = notify(mock_provider.name, required="foo", message="foo")
        assert not rsp.errors
        assert rsp.status is ResponseStatus.SUCCESS
        assert rsp.data == {
            "required": "foo",
            "message": "foo",
            "option_with_default": "foo",
        }

    def test_direct_notify_negative(self):
        with pytest.raises(NoSuchNotifierError, match="No such notifier with name"):
            notify("foo", message="whateverz")
