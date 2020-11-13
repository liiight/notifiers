from abc import ABC
from abc import abstractmethod
from itertools import chain
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

import requests
from pydantic import ValidationError

from notifiers.exceptions import SchemaValidationError
from notifiers.models.response import Response
from notifiers.models.response import ResponseStatus
from notifiers.models.schema import ResourceSchema
from notifiers.models.schema import T_ResourceSchema
from notifiers.utils.helpers import dict_from_environs
from notifiers.utils.helpers import merge_dicts

DEFAULT_ENVIRON_PREFIX = "NOTIFIERS_"


class Resource(ABC):
    """Base class that represent an object holding a schema and its utility methods"""

    name: str
    schema_model: T_ResourceSchema

    def schema(self, by_alias: bool = True) -> dict:
        """Resource's JSON schema as a dict"""
        return self.schema_model.schema(by_alias=by_alias)

    def arguments(self, by_alias: bool = True) -> dict:
        """Resource's arguments"""
        return self.schema(by_alias=by_alias)["properties"]

    @property
    def all_fields(self) -> List[str]:
        """All schema field, including by alias and by attribute name"""
        return list(
            chain(self.arguments().keys(), self.arguments(by_alias=False).keys())
        )

    @property
    def required(self) -> Optional[List[str]]:
        """Resource's required arguments. Note that additional validation may not be represented here"""
        return self.schema().get("required")

    def validate_data(self, data: dict) -> T_ResourceSchema:
        try:
            return self.schema_model.parse_obj(data)
        except ValidationError as e:
            raise SchemaValidationError(validation_error=(str(e)), orig_excp=e) from e

    def create_response(
        self, data: dict = None, response: requests.Response = None, errors: list = None
    ) -> Response:
        """
        Helper function to generate a :class:`~notifiers.core.Response` object

        :param data: The data that was used to send the notification
        :param response: :class:`requests.Response` if exist
        :param errors: List of errors if relevant
        """
        # todo save both original and validated data, add to the response
        status = ResponseStatus.FAILURE if errors else ResponseStatus.SUCCESS
        return Response(
            status=status,
            provider=self.name,
            data=data,
            response=response,
            errors=errors,
        )

    def _get_environs(self, prefix: str) -> dict:
        """
        Fetches set environment variables if such exist, via the :func:`~notifiers.utils.helpers.dict_from_environs`
        Searches for `[PREFIX_NAME]_[PROVIDER_NAME]_[ARGUMENT]` for each of the arguments defined in the schema

        :param prefix: The environ prefix to use. If not supplied, uses the default
        :return: A dict of arguments and value retrieved from environs
        """
        return dict_from_environs(prefix, self.name, self.all_fields)

    def _process_data(self, data: dict) -> T_ResourceSchema:
        """
        The main method that process all resources data. Validates schema, gets environs, validates data, prepares
         it via provider requirements, merges defaults and check for data dependencies

        :param data: The raw data passed by the notifiers client
        :return: Processed data
        """
        env_prefix = data.pop("env_prefix", DEFAULT_ENVIRON_PREFIX)
        environs = self._get_environs(env_prefix)
        data = merge_dicts(data, environs)

        data = self.validate_data(data)
        return data


class ProviderResource(Resource, ABC):
    """The base class that is used to fetch provider related resources like rooms, channels, users etc."""

    @property
    @abstractmethod
    def resource_name(self) -> str:
        pass

    @abstractmethod
    def _get_resource(self, data: ResourceSchema) -> dict:
        pass

    def __call__(self, **kwargs) -> dict:
        data = self._process_data(kwargs)
        return self._get_resource(data)

    def __repr__(self) -> str:
        return f"<ProviderResource,provider={self.name},resource={self.resource_name}>"


T_ProviderResource = TypeVar("T_ProviderResource", bound=ProviderResource)


class Provider(Resource, ABC):
    """The Base class all notification providers inherit from."""

    _resources: Dict[str, T_ProviderResource] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        provider_registry[cls.name] = cls

    def __repr__(self):
        return f"<Provider({self.name.capitalize()})>"

    def __getattr__(self, item):
        if item in self._resources:
            return self._resources[item]
        raise AttributeError(f"{self} does not have a property {item}")

    @property
    def base_url(self) -> str:
        return ""

    @property
    @abstractmethod
    def site_url(self) -> str:
        pass

    @property
    def metadata(self) -> dict:
        """
        Returns a dict of the provider metadata as declared. Override if needed.
        """
        return {"base_url": self.base_url, "site_url": self.site_url, "name": self.name}

    @property
    def resources(self) -> List[str]:
        """Return a list of names of relevant :class:`~notifiers.core.ProviderResource` objects"""
        return list(self._resources.keys())

    @abstractmethod
    def _send_notification(self, data: ResourceSchema) -> Response:
        """
        The core method to trigger the provider notification. Must be overridden.

        :param data: Notification data
        """

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
        data = self._process_data(kwargs)
        rsp = self._send_notification(data)
        if raise_on_errors:
            rsp.raise_on_errors()
        return rsp


T_Provider = TypeVar("T_Provider", bound=Provider)


provider_registry: Dict[str, Type[T_Provider]] = {}
