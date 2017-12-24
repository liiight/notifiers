import os
import logging

import jsonschema
from jsonschema.exceptions import best_match
import requests

from .exceptions import SchemaError, BadArguments, NotificationError

DEFAULT_ENVIRON_PREFIX = 'NOTIFIERS_'

log = logging.getLogger('notifiers')


class Response:
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


class Provider:
    base_url = ''
    site_url = ''
    provider_name = ''

    def __repr__(self):
        return f'<Provider:[{self.provider_name.capitalize()}]>'

    @property
    def schema(self) -> dict:
        """
        A property method that'll hold the provider schema.
        Schema MUST be an object and this method must be overridden

        :return: JSON schema of the provider
        """
        raise NotImplementedError

    @property
    def metadata(self) -> dict:
        """
        Returns a dict of the provider metadata as declared.. Override if needed.
        """
        return {
            'base_url': self.base_url,
            'site_url': self.site_url,
            'provider_name': self.provider_name
        }

    @property
    def arguments(self) -> dict:
        """
        Returns all of the provider argument as declared in the JSON schema
        """
        return dict(self.schema['properties'].items())

    @property
    def required(self) -> list:
        """
        Return a list of the required provider arguments. By default, it tries to access the ``required``
         property of the JSON schema. If such a property doesn't exist (perhaps required is enforced via a
          sophisticated schema form), override this method to return the correct list of required arguments.
        """
        return self.schema.get('required', [])

    @property
    def defaults(self) -> dict:
        """
        A dict of default provider values if such is needed.
        """
        return {}

    def _merge_dict_into_dict(self, target_dict: dict, merge_dict: dict) -> dict:
        """
        Merges ``merge_dict`` into ``target_dict`` if the latter does not already contain a value for each of the key
        names in ``merge_dict``. Used to cleanly merge default and environ data into notification payload.

        :param target_dict: The target dict to merge into and return, the user provided data for example
        :param merge_dict: The data that should be merged into the target data
        :return: A dict of merged data
        """
        # todo move this into utils
        log.debug('merging dict %s into %s', merge_dict, target_dict)
        for key, value in merge_dict.items():
            if key not in target_dict:
                target_dict[key] = value
        return target_dict

    def _merge_defaults(self, data: dict) -> dict:
        """
        Convenience method that calls :function:``_merge_dict_into_dict`` in order to merge default values

        :param data: Notification data
        :return: A merged dict of provided data with added defaults
        """
        log.debug('merging defaults %s into data %s', self.defaults, data)
        return self._merge_dict_into_dict(data, self.defaults)

    def _get_environs(self, prefix: str = None) -> dict:
        """
        Fetches set environment variables if such exist.
        Searches for `[PREFIX_NAME]_[PROVIDER_NAME]_[ARGUMENT]` for each of the arguments defined in the schema

        :param prefix: The environ prefix to use. If not supplied, uses the default
        :return: A dict of arguments and value retrieved from environs
        """
        if not prefix:
            log.debug('using default environ prefix')
            prefix = DEFAULT_ENVIRON_PREFIX
        environs = {}
        log.debug('starting to collect environs using prefix: \'%s\'', prefix)
        for arg in self.arguments:
            environ = f'{prefix}{self.provider_name}_{arg}'.upper()
            if os.environ.get(environ):
                environs[arg] = os.environ[environ]
        return environs

    def _prepare_data(self, data: dict) -> dict:
        """
        Use this method to manipulate data that'll fit the respected provider API.
         For example, all provider must use the ``message`` argument but sometimes provider expects a different
         variable name for this, like ``text``.

        :param data: Notification data
        :return: Returns manipulated data, if there's a need for such manipulations.
        """
        return data

    def _send_notification(self, data: dict) -> Response:
        """
        The core method to trigger the provider notification. Must be overridden.

        :param data: Notification data
        :return: Returns a :class:``Response`` object
        """
        raise NotImplementedError

    def _validate_schema(self, validator: jsonschema.Draft4Validator):
        """
        Validates provider schema for syntax issues. Raises :class:`SchemaError` if relevant

        :param validator: :class:`jsonschema.Draft4Validator`
        """
        try:
            log.debug('validating provider schema')
            validator.check_schema(self.schema)
        except jsonschema.SchemaError as e:
            # todo generate custom errors when relevant
            raise SchemaError(schema_error=e.message, provider=self.provider_name, data=self.schema)

    def _validate_data(self, data: dict, validator: jsonschema.Draft4Validator):
        """
        Validates data against provider schema. Raises :class:`BadArguments` if relevant

        :param data: Data to validate
        :param validator: :class:`jsonschema.Draft4Validator`
        """
        log.debug('validating provided data')
        e = best_match(validator.iter_errors(data))
        if e:
            raise BadArguments(validation_error=e.message, provider=self.provider_name, data=data)

    def notify(self, **kwargs: dict) -> Response:
        validator = jsonschema.Draft4Validator(self.schema)
        self._validate_schema(validator)

        env_prefix = kwargs.pop('env_prefix', None)
        environs = self._get_environs(env_prefix)
        if environs:
            kwargs = self._merge_dict_into_dict(kwargs, environs)

        self._validate_data(kwargs, validator)
        data = self._prepare_data(kwargs)
        data = self._merge_defaults(data)
        return self._send_notification(data)


# Avoid premature import
from .providers import _all_providers


def get_notifier(provider_name: str) -> Provider:
    """
    Convenience method to return an instantiated :class:`Provider` object according to it ``provider_name``

    :param provider_name: The ``provider_name`` of the requested :class:`Provider`
    :return: :class:``Provider`` or None
    """
    if provider_name in _all_providers:
        log.debug('found a match for \'%s\', returning', provider_name)
        return _all_providers[provider_name]()


def all_providers() -> list:
    """
    Returns a list of all :class:`Provider` names

    """
    return list(_all_providers.keys())
