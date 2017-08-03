import jsonschema
import requests

from .exceptions import SchemaError, BadArguments, NotificationError


class NotificationResponse(object):
    def __init__(self, status: str, provider: str, data: dict, response: requests.Response = None, errors: list = None):
        self.status = status
        self.provider = provider
        self.data = data
        self.response = response
        self.errors = errors

    def __repr__(self):
        return f'<NotificationResponse,{self.provider.capitalize()},status={self.status}>'

    def raise_on_errors(self):
        if self.errors:
            raise NotificationError(provider=self.provider, data=self.data, errors=self.errors)


class NotificationProvider(object):
    base_url = ''
    site_url = ''
    provider_name = ''
    schema = {}

    def __repr__(self):
        return f'<NotificationProvider:[{self.provider_name.capitalize()}]>'

    @property
    def metadata(self) -> dict:
        return {
            'base_url': self.base_url,
            'site_url': self.site_url,
            'provider_name': self.provider_name
        }

    @property
    def arguments(self) -> dict:
        return dict(self.schema['properties'].items())

    @property
    def required(self) -> list:
        return self.schema.get('required', [])

    def _prepare_data(self, data: dict) -> dict:
        return

    def _send_notification(self, data: dict):
        raise NotImplementedError

    def _validate_data(self, data: dict):
        try:
            validator = jsonschema.Draft4Validator(self.schema)
            validator.check_schema(self.schema)
            validator.validate(data)
        except jsonschema.SchemaError as e:
            raise SchemaError(schema_error=e.message, provider=self.provider_name, data=self.schema)
        except jsonschema.ValidationError as e:
            raise BadArguments(validation_error=e.message, provider=self.provider_name, data=data)

    def notify(self, **kwargs: dict) -> NotificationResponse:
        self._validate_data(kwargs)
        data = self._prepare_data(kwargs)
        return self._send_notification(data)


# Avoid premature import
from .providers import _all_providers


def get_notifier(provider_name: str) -> NotificationProvider:
    return _all_providers.get(provider_name)()


def all_providers() -> list:
    return list(_all_providers.keys())
