from functools import partial

import click

from notifiers import __version__, get_notifier
from notifiers.core import all_providers
from notifiers.exceptions import NotifierException
from notifiers_cli.utils.dynamic_click import (
    schema_to_command, CORE_COMMANDS
)
from notifiers_cli.utils.callbacks import func_factory, _notify, _resource, _resources


def provider_group_factory():
    """Dynamically generate provider groups for all providers, and add all basic command to it"""
    for provider in all_providers():
        p = get_notifier(provider)
        provider_name = p.name
        help = f"Options for '{provider_name}'"
        group = click.Group(name=provider_name, help=help)

        # Notify command
        notify = partial(_notify, p=p)
        group.add_command(schema_to_command(p, 'notify', notify, add_message=True))

        # Resources command
        resources_callback = partial(_resources, p=p)
        resources_cmd = click.Command('resources', callback=resources_callback, help='Show provider resources list')
        group.add_command(resources_cmd)

        pretty_opt = click.Option(['--pretty/--not-pretty'], help='Output a pretty version of the JSON')

        # Add any provider resources
        for resource in p.resources:
            rsc = getattr(p, resource)
            rsrc_callback = partial(_resource, rsc)
            rsrc_command = schema_to_command(rsc, resource, rsrc_callback, add_message=False)
            rsrc_command.params.append(pretty_opt)
            group.add_command(rsrc_command)

        for name, description in CORE_COMMANDS.items():
            callback = func_factory(p, name)
            params = [pretty_opt]
            command = click.Command(name, callback=callback, help=description.format(provider_name), params=params)
            group.add_command(command)

        notifiers_cli.add_command(group)


@click.group()
@click.version_option(version=__version__, prog_name='notifiers', message=('%(prog)s %(version)s'))
@click.option('--env-prefix', help='Set a custom prefix for env vars usage')
@click.pass_context
def notifiers_cli(ctx, env_prefix):
    """Notifiers CLI operation"""
    ctx.obj['env_prefix'] = env_prefix


@notifiers_cli.command()
def providers():
    """Shows all available providers"""
    click.echo(', '.join(all_providers()))


def entry_point():
    """The entry that CLI is executed from"""
    try:
        provider_group_factory()
        notifiers_cli(obj={})
    except NotifierException as e:
        click.secho(f'ERROR: {e.message}', bold=True, fg='red')
        exit(1)


if __name__ == '__main__':
    entry_point()
