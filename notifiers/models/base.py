from __future__ import annotations

import copy
from typing import Any, ClassVar

from pydantic import AliasChoices, BaseModel, ConfigDict, ValidationError
from pydantic.fields import FieldInfo
from pydantic_core import PydanticCustomError, PydanticUndefined

from .types import UNION_TAGS


class SchemaModel(BaseModel):
    """
    Base class for all provider and resource schemas.

    - Unknown arguments are rejected (``extra="forbid"``). Providers that pass unknown arguments through to their API
      override this with ``extra="allow"``.
    - Fields can be populated by their name or their alias. Python attribute names are snake_case, the alias holds the
      name the remote API (or the pre 2.0 argument) uses, e.g. ``device_id`` with alias ``deviceId``.
    - Model building is deferred until first use, which keeps ``import notifiers`` fast.

    Cross field rules are regular pydantic ``@model_validator`` methods. The helpers below make the common ones short.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_by_name=True,
        validate_by_alias=True,
        defer_build=True,
    )

    required_with_default: ClassVar[frozenset[str]] = frozenset()
    """Field names the service requires, but which have a default so they never need to be passed explicitly"""

    def is_set(self, name: str) -> bool:
        """Whether the field ``name`` was passed with a non ``None`` value"""
        return name in self.model_fields_set and getattr(self, name) is not None

    def require_dependencies(self, dependencies: dict[str, list[str]]):
        """
        Raises if a field was passed without the fields it depends on

        :param dependencies: ``{"a": ["b"]}`` means that if ``a`` is passed, ``b`` must be passed too. Field names
        """
        for name, required in dependencies.items():
            if not self.is_set(name):
                continue
            for dependency in required:
                if not self.is_set(dependency):
                    raise PydanticCustomError(
                        "dependency",
                        "'{dependency}' is a dependency of '{name}'",
                        {"dependency": argument_name(type(self), dependency), "name": argument_name(type(self), name)},
                    )


def argument_name(model: type[SchemaModel], name: str) -> str:
    """The name an argument is exposed under (its alias if set) for a field name"""
    return field_key(name, model.model_fields[name])


def field_key(name: str, field: FieldInfo) -> str:
    """The key a field is exposed under in processed data, defaults and ``required``: its alias if set, else its name"""
    return field.serialization_alias or field.alias or name


def field_names(name: str, field: FieldInfo) -> list[str]:
    """All the keys a field accepts as input, preferred key first"""
    names = [field_key(name, field), name]
    if isinstance(field.validation_alias, AliasChoices):
        names += [choice for choice in field.validation_alias.choices if isinstance(choice, str)]
    elif isinstance(field.validation_alias, str):
        names.append(field.validation_alias)
    return list(dict.fromkeys(names))


def required_fields(model: type[SchemaModel]) -> list[str]:
    """
    Names (aliases where set) of the required fields, in declaration order: fields without a default, plus fields
    listed in the model's ``required_with_default``
    """
    return [field_key(name, field) for name, field in model.model_fields.items() if field.is_required() or name in model.required_with_default]


def model_defaults(model: type[SchemaModel], keys: set[str] | None = None) -> dict:
    """
    A dict of the non-``None`` default values declared on a model, keyed by :func:`field_key`.
    Fields with a ``default_factory`` are included, the factory is called each time.

    :param model: The model to get defaults of
    :param keys: Only include these keys. Factories of other fields are not called
    """
    defaults = {}
    for name, field in model.model_fields.items():
        if keys is not None and field_key(name, field) not in keys:
            continue
        if field.default_factory is not None:
            value = field.default_factory()
        elif field.default is PydanticUndefined:
            continue
        else:
            value = copy.deepcopy(field.default)
        if value is not None:
            defaults[field_key(name, field)] = value
    return defaults


def format_validation_error(error: ValidationError) -> str:
    """
    Converts a pydantic :class:`~pydantic.ValidationError` into a short, single line message describing the first
    error. All errors remain available via ``error.errors()``.
    """
    errors = error.errors(include_url=False)
    # Prefer "missing" errors, so the message names a missing required argument rather than a less relevant error
    first = next((e for e in errors if e["type"] == "missing"), errors[0])
    loc = ".".join(str(part) for part in first["loc"] if part not in UNION_TAGS)
    msg = first["msg"]
    if first["type"] == "value_error":
        msg = msg.removeprefix("Value error, ")
    if first["type"] == "missing":
        return f"'{loc}' is a required property"
    if first["type"] == "extra_forbidden":
        return f"Additional properties are not allowed ('{loc}' was unexpected)"
    if not loc:
        return msg
    return f"'{loc}': {msg}"


def validation_errors(error: ValidationError) -> list[dict[str, Any]]:
    """JSON serializable list of all validation errors"""
    return [
        {"loc": [p for p in e["loc"] if p not in UNION_TAGS], "msg": e["msg"], "type": e["type"]}
        for e in error.errors(include_url=False, include_context=False, include_input=False)
    ]
