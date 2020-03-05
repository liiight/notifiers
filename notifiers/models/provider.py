import json
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import requests
from pydantic import BaseModel
from pydantic import Extra
from pydantic import ValidationError

from notifiers.exceptions import BadArguments
from notifiers.models.response import Response
from notifiers.models.response import ResponseStatus
from notifiers.utils.helpers import dict_from_environs
from notifiers.utils.helpers import merge_dicts

DEFAULT_ENVIRON_PREFIX = "NOTIFIERS_"


class SchemaModel(BaseModel):
    """The base class for Schemas"""

    @staticmethod
    def to_list(value: Union[Any, List[Any]]) -> List[Any]:
        """Helper method to make sure a return value is a list"""
        if not isinstance(value, list):
            return [value]
        return value

    @staticmethod
    def to_comma_separated(values: Union[Any, List[Any]]) -> str:
        """Helper method that return a comma separates string from a value"""
        if not isinstance(values, list):
            values = [values]
        return ",".join(str(value) for value in values)

    @staticmethod
    def one_or_more_of(type_: Any) -> Union[List[Any], Any]:
        """A helper method that returns the relevant type to specify that one or more of the given type can be used
         in a schema"""
        return Union[List[type_], type_]

    def to_dict(
        self, exclude_none: bool = True, by_alias: bool = True, **kwargs
    ) -> dict:
        """
        A helper method to a very common dict builder.
        Round tripping to json and back to dict is needed since the model can contain special object that need
         to be transformed to json first (like enums)

        :param exclude_none: Should values that are `None` be part of the payload
        :param by_alias: Use the field name of its alias name (if exists)
        :param kwargs: Additional options. See https://pydantic-docs.helpmanual.io/usage/exporting_models/
        :return: dict payload of the schema
        """
        return json.loads(
            self.json(exclude_none=exclude_none, by_alias=by_alias, **kwargs)
        )

    class Config:
        allow_population_by_field_name = True
        extra = Extra.forbid


class SchemaResource(ABC):
    """Base class that represent an object schema and its utility methods"""

    schema_model: SchemaModel

    @property
    @abstractmethod
    def name(self) -> str:
        """Resource provider name"""

    @property
    def schema(self) -> dict:
        """Resource's JSON schema as a dict"""
        return self.schema_model.schema()

    @property
    def arguments(self) -> dict:
        """Resource's arguments"""
        return self.schema["properties"]

    @property
    def required(self) -> Optional[List[str]]:
        """Resource's required arguments. Note that additional validation may not be represented here"""
        return self.schema.get("required")

    def validate_data(self, data: dict) -> SchemaModel:
        try:
            return self.schema_model.parse_obj(data)
        except ValidationError as e:
            raise BadArguments(validation_error=(str(e)), orig_excp=e)

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
        return dict_from_environs(prefix, self.name, list(self.arguments.keys()))

    def _process_data(self, data: dict) -> SchemaModel:
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
    def _send_notification(self, data: SchemaModel) -> Response:
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
        data = self._process_data(kwargs)
        return self._get_resource(data)

    def __repr__(self):
        return f"<ProviderResource,provider={self.name},resource={self.resource_name}>"
