import os

import jsonschema
import requests

from .exceptions import SchemaError, BadArguments, NotificationError

DEFAULT_ENVIRON_PREFIX = 'NOTIFIERS_'


class Response(object):
    """
    A wrapper for the Notification response.

    :param status: Response status string. ``SUCCESS`` or ``FAILED``
    :param provider: Provider name that returned that response.
     Correlates to :class:``Provider.provider_name``
    :param data: The notification data that was used for the notification
    :param response: The response object that was returned. Usually :class:`requests.Response`
    :param errors: Holds a list of errors if relevant
    """

    def __init__(self, status: str, provider: str, data: dict, response: requests.Response = None, errors: list = None):
        self.status = status
        self.provider = provider
        self.data = data
        self.response = response
        self.errors = errors

    def __repr__(self):
        return f'<Response,provider={self.provider.capitalize()},status={self.status}>'

    def raise_on_errors(self):
        """
        Raises a :class:`NotificationError` if response hold errors

        :raise NotificationError:
        """
        if self.errors:
            raise NotificationError(provider=self.provider, data=self.data, errors=self.errors)


class Provider(object):
    base_url = ''
    site_url = ''
    provider_name = ''

    def __repr__(self):
        return f'<Provider:[{self.provider_name.capitalize()}]>'

    @property
    def schema(self):
        raise NotImplementedError

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

    def _get_environs(self, prefix: str = None) -> dict:
        if not prefix:
            prefix = DEFAULT_ENVIRON_PREFIX
        environs = {}
        for arg in self.arguments:
            environ = f'{prefix}{self.provider_name}_{arg}'.upper()
            if os.environ.get(environ):
                environs[arg] = os.environ[environ]
        return environs

    def _prepare_data(self, data: dict) -> dict:
        return

    def _send_notification(self, data: dict):
        raise NotImplementedError

    def _validate_schema(self, validator: jsonschema.Draft4Validator):
        try:
            validator.check_schema(self.schema)
        except jsonschema.SchemaError as e:
            raise SchemaError(schema_error=e.message, provider=self.provider_name, data=self.schema)

    def _validate_data(self, data: dict, validator: jsonschema.Draft4Validator):
        try:
            validator.validate(data)
        except jsonschema.ValidationError as e:
            raise BadArguments(validation_error=e.message, provider=self.provider_name, data=data)

    def notify(self, **kwargs: dict) -> Response:
        validator = jsonschema.Draft4Validator(self.schema)
        self._validate_schema(validator)

        env_prefix = kwargs.pop('env_prefix', None)
        environs = self._get_environs(env_prefix)
        if environs:
            kwargs = {**kwargs, **environs}

        self._validate_data(kwargs, validator)
        data = self._prepare_data(kwargs)
        return self._send_notification(data)


# Avoid premature import
from .providers import _all_providers


def get_notifier(provider_name: str) -> Provider:
    return _all_providers.get(provider_name)()


def all_providers() -> list:
    return list(_all_providers.keys())
