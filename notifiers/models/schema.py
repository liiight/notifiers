import json
from typing import Any
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from pydantic import Extra
from pydantic import NameEmail


class ResourceSchema(BaseModel):
    """The base class for Schemas"""

    _values_to_exclude: Tuple[str, ...] = ()

    @staticmethod
    def to_list(value: Union[Any, List[Any]]) -> List[Any]:
        """Helper method to make sure a return value is a list"""
        if not isinstance(value, list):
            return [value]
        return value

    @classmethod
    def to_comma_separated(cls, values: Union[Any, List[Any]]) -> str:
        """Helper method that return a comma separates string from a value"""
        values = cls.to_list(values)
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
            self.json(
                exclude_none=exclude_none,
                by_alias=by_alias,
                exclude=set(self._values_to_exclude),
                **kwargs,
            )
        )

    class Config:
        allow_population_by_field_name = True
        extra = Extra.forbid
        json_encoders = {NameEmail: lambda e: str(e)}


T_ResourceSchema = TypeVar("T_ResourceSchema", bound=ResourceSchema)
