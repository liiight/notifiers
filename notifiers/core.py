import logging
from abc import ABC
from abc import abstractmethod

import jsonschema
import requests
from jsonschema.exceptions import best_match

from .exceptions import BadArguments
from .exceptions import NoSuchNotifierError
from .exceptions import NotificationError
from .exceptions import SchemaError
from .utils.helpers import dict_from_environs
from .utils.helpers import merge_dicts
from .utils.schema.formats import format_checker

DEFAULT_ENVIRON_PREFIX = "NOTIFIERS_"

log = logging.getLogger("notifiers")

FAILURE_STATUS = "Failure"
SUCCESS_STATUS = "Success"


class Response:
    """
    A wrapper for the Notification response.

    :param status: Response status string. ``SUCCESS`` or ``FAILED``
    :param provider: Provider name that returned that response. Correlates to :attr:`~notifiers.core.Provider.name`
    :param data: The notification data that was used for the notification
    :param response: The response object that was returned. Usually :class:`requests.Response`
    :param errors: Holds a list of errors if relevant
    """

    def __init__(
        self,
        status: str,
        provider: str,
        data: dict,
        response: requests.Response = None,
        errors: list = None,
    ):
        self.status = status
        self.provider = provider
        self.data = data
        self.response = response
        self.errors = errors

    def __repr__(self):
        return f"<Response,provider={self.provider.capitalize()},status={self.status}, errors={self.errors}>"

    def raise_on_errors(self):
        """
        Raises a :class:`~notifiers.exceptions.NotificationError` if response hold errors

        :raises: :class:`~notifiers.exceptions.NotificationError`: If response has errors
        """
        if self.errors:
            raise NotificationError(
                provider=self.provider,
                data=self.data,
                errors=self.errors,
                response=self.response,
            )

    @property
    def ok(self):
        return self.errors is None


class SchemaResource(ABC):
    """Base class that represent an object schema and its utility methods"""

    @property
    @abstractmethod
    def _required(self) -> dict:
        """Will hold the schema's required part"""
        pass

    @property
    @abstractmethod
    def _schema(self) -> dict:
        """Resource JSON schema without the required part"""
        pass

    _merged_schema = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Resource provider name"""
        pass

    @property
    def schema(self) -> dict:
        """
        A property method that'll return the constructed provider schema.
        Schema MUST be an object and this method must be overridden

        :return: JSON schema of the provider
        """
        if not self._merged_schema:
            log.debug("merging required dict into schema for %s", self.name)
            self._merged_schema = self._schema.copy()
            self._merged_schema.update(self._required)
        return self._merged_schema

    @property
    def arguments(self) -> dict:
        """Returns all the provider argument as declared in the JSON schema"""
        return dict(self.schema["properties"].items())

    @property
    def required(self) -> dict:
        """Returns a dict of the relevant required parts of the schema"""
        return self._required

    @property
    def defaults(self) -> dict:
        """A dict of default provider values if such is needed"""
        return {}

    def create_response(
        self, data: dict = None, response: requests.Response = None, errors: list = None
    ) -> Response:
        """
        Helper function to generate a :class:`~notifiers.core.Response` object

        :param data: The data that was used to send the notification
        :param response: :class:`requests.Response` if exist
        :param errors: List of errors if relevant
        """
        status = FAILURE_STATUS if errors else SUCCESS_STATUS
        return Response(
            status=status,
            provider=self.name,
            data=data,
            response=response,
            errors=errors,
        )

    def _merge_defaults(self, data: dict) -> dict:
        """
        Convenience method that calls :func:`~notifiers.utils.helpers.merge_dicts` in order to merge
        default values

        :param data: Notification data
        :return: A merged dict of provided data with added defaults
        """
        log.debug("merging defaults %s into data %s", self.defaults, data)
        return merge_dicts(data, self.defaults)

    def _get_environs(self, prefix: str = None) -> dict:
        """
        Fetches set environment variables if such exist, via the :func:`~notifiers.utils.helpers.dict_from_environs`
        Searches for `[PREFIX_NAME]_[PROVIDER_NAME]_[ARGUMENT]` for each of the arguments defined in the schema

        :param prefix: The environ prefix to use. If not supplied, uses the default
        :return: A dict of arguments and value retrieved from environs
        """
        if not prefix:
            log.debug("using default environ prefix")
            prefix = DEFAULT_ENVIRON_PREFIX
        return dict_from_environs(prefix, self.name, list(self.arguments.keys()))

    def _prepare_data(self, data: dict) -> dict:
        """
        Use this method to manipulate data that'll fit the respected provider API.
         For example, all provider must use the ``message`` argument but sometimes provider expects a different
         variable name for this, like ``text``.

        :param data: Notification data
        :return: Returns manipulated data, if there's a need for such manipulations.
        """
        return data

    def _validate_schema(self):
        """
        Validates provider schema for syntax issues. Raises :class:`~notifiers.exceptions.SchemaError` if relevant

        :raises: :class:`~notifiers.exceptions.SchemaError`
        """
        try:
            log.debug("validating provider schema")
            self.validator.check_schema(self.schema)
        except jsonschema.SchemaError as e:
            raise SchemaError(
                schema_error=e.message, provider=self.name, data=self.schema
            )

    def _validate_data(self, data: dict):
        """
        Validates data against provider schema. Raises :class:`~notifiers.exceptions.BadArguments` if relevant

        :param data: Data to validate
        :raises: :class:`~notifiers.exceptions.BadArguments`
        """
        log.debug("validating provided data")
        e = best_match(self.validator.iter_errors(data))
        if e:
            custom_error_key = f"error_{e.validator}"
            msg = (
                e.schema[custom_error_key]
                if e.schema.get(custom_error_key)
                else e.message
            )
            raise BadArguments(validation_error=msg, provider=self.name, data=data)

    def _validate_data_dependencies(self, data: dict) -> dict:
        """
        Validates specific dependencies based on the content of the data, as opposed to its structure which can be
        verified on the schema level

        :param data: Data to validate
        :return: Return data if its valid
        :raises: :class:`~notifiers.exceptions.NotifierException`
        """
        return data

    def _process_data(self, **data) -> dict:
        """
        The main method that process all resources data. Validates schema, gets environs, validates data, prepares
         it via provider requirements, merges defaults and check for data dependencies

        :param data: The raw data passed by the notifiers client
        :return: Processed data
        """
        env_prefix = data.pop("env_prefix", None)
        environs = self._get_environs(env_prefix)
        if environs:
            data = merge_dicts(data, environs)

        data = self._merge_defaults(data)
        self._validate_data(data)
        data = self._validate_data_dependencies(data)
        data = self._prepare_data(data)
        return data

    def __init__(self):
        self.validator = jsonschema.Draft4Validator(
            self.schema, format_checker=format_checker
        )
        self._validate_schema()


class Provider(SchemaResource, ABC):
    """The Base class all notification providers inherit from."""

    _resources = {}

    def __repr__(self):
        return f"<Provider:[{self.name.capitalize()}]>"

    def __getattr__(self, item):
        if item in self._resources:
            return self._resources[item]
        raise AttributeError(f"{self} does not have a property {item}")

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def site_url(self):
        pass

    @property
    def metadata(self) -> dict:
        """
        Returns a dict of the provider metadata as declared. Override if needed.
        """
        return {"base_url": self.base_url, "site_url": self.site_url, "name": self.name}

    @property
    def resources(self) -> list:
        """Return a list of names of relevant :class:`~notifiers.core.ProviderResource` objects"""
        return list(self._resources.keys())

    @abstractmethod
    def _send_notification(self, data: dict) -> Response:
        """
        The core method to trigger the provider notification. Must be overridden.

        :param data: Notification data
        """
        pass

    def notify(self, raise_on_errors: bool = False, **kwargs) -> Response:
        """
        The main method to send notifications. Prepares the data via the
        :meth:`~notifiers.core.SchemaResource._prepare_data` method and then sends the notification
        via the :meth:`~notifiers.core.Provider._send_notification` method

        :param kwargs: Notification data
        :param raise_on_errors: Should the :meth:`~notifiers.core.Response.raise_on_errors` be invoked immediately
        :return: A :class:`~notifiers.core.Response` object
        :raises: :class:`~notifiers.exceptions.NotificationError` if ``raise_on_errors`` is set to True and response
         contained errors
        """
        data = self._process_data(**kwargs)
        rsp = self._send_notification(data)
        if raise_on_errors:
            rsp.raise_on_errors()
        return rsp


class ProviderResource(SchemaResource, ABC):
    """The base class that is used to fetch provider related resources like rooms, channels, users etc."""

    @property
    @abstractmethod
    def resource_name(self):
        pass

    @abstractmethod
    def _get_resource(self, data: dict):
        pass

    def __call__(self, **kwargs):
        data = self._process_data(**kwargs)
        return self._get_resource(data)

    def __repr__(self):
        return f"<ProviderResource,provider={self.name},resource={self.resource_name}>"


# Avoid premature import
from .providers import _all_providers  # noqa: E402


def get_notifier(provider_name: str, strict: bool = False) -> Provider:
    """
    Convenience method to return an instantiated :class:`~notifiers.core.Provider` object according to it ``name``

    :param provider_name: The ``name`` of the requested :class:`~notifiers.core.Provider`
    :param strict: Raises a :class:`ValueError` if the given provider string was not found
    :return: :class:`Provider` or None
    :raises ValueError: In case ``strict`` is True and provider not found
    """
    if provider_name in _all_providers:
        log.debug("found a match for '%s', returning", provider_name)
        return _all_providers[provider_name]()
    elif strict:
        raise NoSuchNotifierError(name=provider_name)


def all_providers() -> list:
    """Returns a list of all :class:`~notifiers.core.Provider` names"""
    return list(_all_providers.keys())


def notify(provider_name: str, **kwargs) -> Response:
    """
    Quickly sends a notification without needing to get a notifier via the :func:`get_notifier` method.

    :param provider_name: Name of the notifier to use. Note that if this notifier name does not exist it will raise a
    :param kwargs: Notification data, dependant on provider
    :return: :class:`Response`
    :raises: :class:`~notifiers.exceptions.NoSuchNotifierError` If ``provider_name`` is unknown,
     will raise notification error
    """
    return get_notifier(provider_name=provider_name, strict=True).notify(**kwargs)
