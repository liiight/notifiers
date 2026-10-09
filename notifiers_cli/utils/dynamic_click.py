"""
Helper module with tools to dynamically convert :class:`~notifiers.core.Provider` and
:class:`~notifiers.core.ProviderResource` schema models to :mod:`click` commands
"""

from __future__ import annotations

import types
import typing
from collections.abc import Callable
from typing import Annotated, Any, Literal, Union

import click
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from notifiers.models.base import field_key

CORE_COMMANDS = {
    "required": "'{}' required schema",
    "schema": "'{}' full schema",
    "metadata": "'{}' metadata",
    "defaults": "'{}' default values",
}

PRIMITIVE_TYPES: dict[type, click.ParamType] = {
    str: click.STRING,
    int: click.INT,
    float: click.FLOAT,
    bool: click.BOOL,
}


def _strip_annotated(annotation: Any) -> Any:
    while typing.get_origin(annotation) is Annotated:
        annotation = typing.get_args(annotation)[0]
    return annotation


def _union_members(annotation: Any) -> list[Any]:
    """The members of a union (``X | Y`` or ``Union[X, Y]``) without ``None``, or ``[annotation]`` if it isn't one"""
    annotation = _strip_annotated(annotation)
    if typing.get_origin(annotation) in (Union, types.UnionType):
        members = []
        for arg in typing.get_args(annotation):
            if arg is not type(None):
                members.extend(_union_members(arg))
        return members
    return [annotation]


def _primitive(annotation: Any) -> type | None:
    annotation = _strip_annotated(annotation)
    return annotation if annotation in PRIMITIVE_TYPES else None


def field_to_click_type(field: FieldInfo) -> tuple[click.ParamType | None, bool] | None:
    """
    Maps a pydantic field to a click type

    :param field: The pydantic field
    :return: ``(click_type, multiple)``, ``click_type`` is ``None`` for boolean flags.
     ``None`` if the field can't be expressed on the command line (dicts, nested models, ...)
    """
    members = _union_members(field.annotation)

    # A list, or a value or a list of values (``OneOrMore[T]``): the option can be passed several times
    multiple = any(typing.get_origin(m) is list for m in members)
    items = [typing.get_args(m)[0] if typing.get_origin(m) is list else m for m in members]

    literals = [m for m in items if typing.get_origin(m) is Literal]
    if literals and not multiple:
        choices = [v for literal in literals for v in typing.get_args(literal) if isinstance(v, str)]
        return (click.Choice(choices) if choices else click.BOOL), False

    primitives = {_primitive(m) for m in items}
    if not primitives or None in primitives:
        return None
    if primitives == {bool} and not multiple:
        return None, False
    # Mixed types, e.g. ``str | int``: strings are accepted and converted by the schema model
    primitive = primitives.pop() if len(primitives) == 1 else str
    return PRIMITIVE_TYPES[primitive], multiple


def option_names(name: str, field: FieldInfo) -> list[str]:
    """
    Command line spellings of a field: the argument key (alias if set), plus the snake_case field name when it's spelled
    differently, each as ``--kebab-case`` when written in snake_case and as is otherwise
    """
    names = []
    for key in (field_key(name, field), name.rstrip("_")):
        option = key.replace("_", "-")
        if option not in names:
            names.append(option)
    return names


def _help(field: FieldInfo, multiple: bool) -> str | None:
    description = field.description
    if not description:
        return None
    description = description.strip().capitalize()
    if multiple:
        if not description.endswith("."):
            description += "."
        description += " Multiple usages of this option are allowed"
    return description


def params_factory(model: type[BaseModel], add_message: bool) -> list[click.Parameter]:
    """
    Generates :class:`click.Parameter` objects from a schema model

    :param model: The schema model to operate on
    :param add_message: Whether to add ``message`` as an optional positional argument
    :return: List of created :class:`click.Parameter` objects to be added to a :class:`click.Command`
    """
    params: list[click.Parameter] = []
    if add_message:
        params.append(click.Argument(["message"], required=False))

    for name, field in model.model_fields.items():
        if name == "message":
            continue
        click_type = field_to_click_type(field)
        if click_type is None:
            continue
        param_type, multiple = click_type
        # The callback receives the value under the field's argument key (its alias if set), e.g. ``from`` or ``deviceId``
        dest = field_key(name, field)
        names = option_names(name, field)
        if param_type is None:
            decls = [f"--{option}/--no-{option}" for option in names]
            params.append(click.Option([*decls, dest], default=None, help=_help(field, multiple)))
        else:
            params.append(click.Option([f"--{option}" for option in names] + [dest], type=param_type, multiple=multiple, help=_help(field, multiple)))
    return params


def schema_to_command(p, name: str, callback: Callable, add_message: bool) -> click.Command:
    """
    Generates a :class:`click.Command` from a :class:`~notifiers.core.Provider` or
    :class:`~notifiers.core.ProviderResource` schema model

    :param p: Relevant Provider or ProviderResource
    :param name: Command name
    :param callback: The command callback
    :param add_message: Whether to add ``message`` as an optional positional argument
    :return: A :class:`click.Command`
    """
    params = params_factory(p.schema_model, add_message=add_message)
    return click.Command(name=name, callback=callback, params=params, help=p.__doc__)


def clean_data(data: dict) -> dict:
    """Removes all values that weren't passed (``None`` or empty) and converts tuples into lists"""
    new_data = {}
    for key, value in data.items():
        if value is None:
            continue
        # Multiple value options are passed as tuples, convert to lists to match the schema
        if isinstance(value, tuple):
            if not value:
                continue
            value = list(value)  # noqa: PLW2901
        elif not isinstance(value, bool) and value == "":
            continue
        new_data[key] = value
    return new_data
