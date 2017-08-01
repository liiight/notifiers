import jsonschema
import requests

from notifiers.exceptions import NotificationError
from .exceptions import SchemaError, BadArguments

__all__ = ['get_notifier', 'Provider', 'NotificationResponse', 'providers']


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


class Provider(object):
    base_url = None
    provider_name = None
    schema = {}

    def __repr__(self):
        return f'<Notifier:[{self.provider_name.capitalize()}]>'

    @property
    def arguments(self) -> dict:
        return dict(self.schema['properties'].items())

    @property
    def required(self) -> list:
        return self.schema.get('required', [])

    def _prepare_data(self, data: dict) -> dict:
        raise NotImplementedError

    def _send_notification(self, data: dict):
        raise NotImplementedError

    def _validate_data(self, data: dict):
        try:
            validator = jsonschema.Draft4Validator(data)
            validator.check_schema(data)
            validator.validate(data)
        except jsonschema.SchemaError as e:
            raise SchemaError(e.message)
        except jsonschema.ValidationError as e:
            raise BadArguments(e.message)

    def notify(self, **kwargs: dict) -> NotificationResponse:
        self._validate_data(kwargs)
        data = self._prepare_data(kwargs)
        return self._send_notification(data)


# Avoid circular dependency
from .providers import _all_providers


def get_notifier(provider_name: str) -> Provider:
    return _all_providers.get(provider_name)()


def providers() -> list:
    return list(_all_providers.keys())
