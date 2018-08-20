"""
Callbacks and callback factories to enable dynamically associating :class:`~notifiers.core.Provider` methods to
:class:`click.Group` and :class:`click.Command`
"""
import json
import sys
from functools import partial

import click

from notifiers_cli.utils.dynamic_click import clean_data


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
    message = data.get("message")
    if not message and not sys.stdin.isatty():
        message = click.get_text_stream("stdin").read()
    data["message"] = message

    data = clean_data(data)

    ctx = click.get_current_context()
    if ctx.obj.get("env_prefix"):
        data["env_prefix"] = ctx.obj["env_prefix"]

    rsp = p.notify(**data)
    rsp.raise_on_errors()
    click.secho(f"Succesfully sent a notification to {p.name}!", fg="green")


def _resource(resource, pretty: bool = None, **data):
    """The callback func that will be hooked to the generic resource commands"""
    data = clean_data(data)

    ctx = click.get_current_context()
    if ctx.obj.get("env_prefix"):
        data["env_prefix"] = ctx.obj["env_prefix"]

    rsp = resource(**data)
    dump = partial(json.dumps, indent=4) if pretty else partial(json.dumps)
    click.echo(dump(rsp))


def _resources(p):
    """Callback func to display provider resources"""
    if p.resources:
        click.echo(",".join(p.resources))
    else:
        click.echo(f"Provider '{p.name}' does not have resource helpers")
