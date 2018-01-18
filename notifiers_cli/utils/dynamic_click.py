"""
Helper module with tools to dynamically convert :class:`~notifiers.core.Provider` and
:class:`~notifiers.core.ProviderResource` classes to :mod:`click` data types
"""
from functools import partial

import click

CORE_COMMANDS = {
    'required': "'{}' required schema",
    'schema': "'{}' full schema",
    'metadata': "'{}' metadata",
    'defaults': "'{}' default values",
}
SCHEMA_BASE_MAP = {
    'string': click.STRING,
    'integer': click.INT,
    'number': click.FLOAT,
    'boolean': click.BOOL
}
COMPLEX_TYPES = ['object', 'array']


def handle_oneof(oneof_schema: list) -> tuple:
    """
    Custom handle of `oneOf` JSON schema validator. Tried to match primitive type and see if it should be allowed
     to be passed multiple timns into a command

    :param oneof_schema: `oneOf` JSON schema
    :return: Tuple of :class:`click.ParamType`, ``multiple`` flag and ``description`` of option
    """
    oneof_dict = {schema['type']: schema for schema in oneof_schema}
    click_type = None
    multiple = False
    description = None
    for key, value in oneof_dict.items():
        if key == 'array':
            continue
        elif key in SCHEMA_BASE_MAP:
            if oneof_dict.get('array') and oneof_dict['array']['items']['type'] == key:
                multiple = True
            # Found a match to a primitive type
            click_type = SCHEMA_BASE_MAP[key]
            description = value.get('title')
            break
    return click_type, multiple, description


def json_schema_to_click_type(schema: dict) -> tuple:
    """
    A generic handler of a single property JSON schema to :class:`click.ParamType` converter

    :param schema: JSON schema property to operate on
    :return: Tuple of :class:`click.ParamType`, `description`` of option and optionally a :class:`click.Choice`
     if the allowed values are a closed list (JSON schema ``enum``)
    """
    choices = None
    if isinstance(schema['type'], list):
        if 'string' in schema['type']:
            schema['type'] = 'string'
    click_type = SCHEMA_BASE_MAP[schema['type']]
    description = schema.get('title')
    if schema.get('enum'):
        choices = click.Choice(schema['enum'])
    return click_type, description, choices


def clean_data(data: dict) -> dict:
    """Removes all empty values and converts tuples into lists"""
    new_data = {}
    for key, value in data.items():
        # Verify that only explicitly passed args get passed on
        if not isinstance(value, bool) and not value:
            continue

        # Multiple choice command are passed as tuples, convert to list to match schema
        if isinstance(value, tuple):
            value = list(value)
        new_data[key] = value
    return new_data


def params_factory(schema: dict, add_message: bool) -> list:
    """
    Generates list of :class:`click.Option` based on a JSON schema

    :param schema:  JSON schema to operate on
    :return: Lists of created :class:`click.Option` object to be added to a :class:`click.Command`
    """

    # Immediately create message as an argument
    params = []
    if add_message:
        params.append(click.Argument(['message'], required=False))

    for property, prpty_schema in schema.items():
        multiple = False
        choices = None

        if any(char in property for char in ['@']):
            continue
        if prpty_schema.get('type') in COMPLEX_TYPES:
            continue
        if prpty_schema.get('duplicate'):
            continue
        if property == 'message':
            continue

        elif not prpty_schema.get('oneOf'):
            click_type, description, choices = json_schema_to_click_type(prpty_schema)
        else:
            click_type, multiple, description = handle_oneof(prpty_schema['oneOf'])
            # Not all oneOf schema can be handled by click
            if not click_type:
                continue

        # Convert bool values into flags
        if click_type == click.BOOL:
            param_decls = [get_flag_param_decals_from_bool(property)]
            click_type = None
        else:
            param_decls = [get_param_decals_from_name(property)]

        if description:
            description = description.capitalize()

            if multiple:
                if not description.endswith('.'):
                    description += '.'
                description += ' Multiple usages of this option are allowed'
        # Construct the base command options
        option = partial(click.Option, param_decls=param_decls, help=description, multiple=multiple)

        if choices:
            option = option(type=choices)
        elif click_type:
            option = option(type=click_type)
        else:
            option = option()
        params.append(option)
    return params


def schema_to_command(p, name: str, callback: callable, add_message: bool) -> click.Command:
    """
    Generates a ``notify`` :class:`click.Command` for :class:`~notifiers.core.Provider`

    :param p: Relevant Provider
    :param name: Command name
    :return: A ``notify`` :class:`click.Command`
    """
    params = params_factory(p.schema['properties'], add_message=add_message)
    help = p.__doc__
    cmd = click.Command(name=name, callback=callback, params=params, help=help)
    return cmd


def get_param_decals_from_name(option_name: str) -> str:
    """Converts a name to a param name"""
    name = option_name.replace("_", "-")
    return f'--{name}'


def get_flag_param_decals_from_bool(option_name: str) -> str:
    """Return a '--do/not-do' style flag param"""
    name = option_name.replace("_", "-")
    return f'--{name}/--no-{name}'
