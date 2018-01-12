import json
import sys
from functools import partial

import click

from notifiers_cli.utils.json_schema import COMPLEX_TYPES, json_schema_to_click_type, handle_oneof

CORE_COMMANDS = {
    'required': "'{}' required schema",
    'schema': "'{}' full schema",
    'metadata': "'{}' metadata",
    'defaults': "'{}' default values"
}


def params_factory(schema: dict) -> list:
    """
    Generates list of :class:`click.Option` based on a JSON schema

    :param schema:  JSON schema to operate on
    :return: Lists of created :class:`click.Option` object to be added to a :class:`click.Command`
    """

    # Immediately create message as an argument
    message_arg = click.Argument(['message'], required=False)
    params = [message_arg]

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


def provider_notify_command_factory(p) -> click.Command:
    """
    Generates a ``notify`` :class:`click.Command` for :class:`~notifiers.core.Provider`

    :param p: Relevant Provider
    :return: A ``notify`` :class:`click.Command`
    """
    params = params_factory(p.schema['properties'])
    name = 'notify'
    help = p.__doc__
    notify = partial(_notify, p=p)
    cmd = click.Command(name=name, callback=notify, params=params, help=help)
    return cmd


def func_factory(p, method: str) -> callable:
    """
    Dynamically generates callback commands to correlate to provider public methods

    :param p: A :class:`notifiers.core.Provider` object
    :param method: A string correlating to a provider method
    :return: A callback func
    """

    def callback(pretty: bool = False):
        res = getattr(p, method)
        dump = partial(json.dumps, indent=4) if pretty else partial(json.dumps)
        click.echo(dump(res))

    return callback


def _notify(p, **data):
    """The callback func that will be hooked to the ``notify`` command"""
    message = data.get('message')
    if not message and not sys.stdin.isatty():
        message = click.get_text_stream('stdin').read()
    data['message'] = message

    new_data = {}
    for key, value in data.items():
        # Verify that only explicitly passed args get passed on
        if not isinstance(value, bool) and not value:
            continue

        # Multiple choice command are passed as tuples, convert to list to match schema
        if isinstance(value, tuple):
            value = list(value)
        new_data[key] = value

    ctx = click.get_current_context()
    if ctx.obj.get('env_prefix'):
        new_data['env_prefix'] = ctx.obj['env_prefix']

    rsp = p.notify(**new_data)
    rsp.raise_on_errors()
    click.secho(f'Succesfully sent a notification to {p.provider_name}!', fg='green')


def get_param_decals_from_name(option_name: str) -> str:
    """Converts a name to a param name"""
    name = option_name.replace("_", "-")
    return f'--{name}'


def get_flag_param_decals_from_bool(option_name: str) -> str:
    """Return a '--do/not-do' style flag param"""
    name = option_name.replace("_", "-")
    return f'--{name}/--no-{name}'
