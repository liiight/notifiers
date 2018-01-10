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


def params_factory(schema):
    params = []
    for property, prpty_schema in schema.items():
        multiple = False
        choices = None
        if prpty_schema.get('type') and any(char in property for char in ['@']) \
                or prpty_schema.get('type') in COMPLEX_TYPES or prpty_schema.get('duplicate'):
            continue
        elif not prpty_schema.get('oneOf'):
            click_type, description, choices = json_schema_to_click_type(prpty_schema)
        else:
            click_type, multiple, description = handle_oneof(prpty_schema['oneOf'])
            if not click_type:
                continue
        param_decls = [get_param_decals_from_name(property)]
        if description:
            description = description.capitalize()
        option = partial(click.Option, param_decls=param_decls, help=description, multiple=multiple)
        if choices:
            option = option(type=choices)
        else:
            option = option(type=click_type)
        params.append(option)
    return params


def provider_notify_command_factory(p):
    """
    Generates a ``notify`` :class:`click.Command` for :class:`~notifiers.core.Provider`

    :param p: Relevant Provider
    :return: A ``notify`` :class:`click.Command`
    :rtype: :class:`click.Command`
    """
    params = params_factory(p.schema['properties'])
    name = 'notify'
    help = p.__doc__
    notify = partial(_notify, p=p)
    cmd = click.Command(name=name, callback=notify, params=params, help=help)
    return cmd


def func_factory(p, method):
    """
    Dynamically generates callback commands to correlate to
    :param p:
    :param method:
    :return:
    """

    def callback():
        meth = getattr(p, method)
        pretty = json.dumps(meth, indent=4)
        click.echo(pretty)

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
        if isinstance(value, tuple):
            value = list(value)
        new_data[key] = value

    rsp = p.notify(**new_data)
    rsp.raise_on_errors()


def get_param_decals_from_name(option_name):
    return f'--{option_name.replace("_", "-")}'
