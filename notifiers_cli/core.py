import click

from notifiers import __version__, get_notifier
from notifiers.core import all_providers
from notifiers.exceptions import NotifierException
from notifiers_cli.utils.dynamic_click import provider_notify_command_factory, CORE_COMMANDS, func_factory


def provider_group_factory():
    """Dynamically generate provider groups for all providers, and add all basic command to it"""
    for provider in all_providers():
        p = get_notifier(provider)
        provider_name = p.provider_name
        help = f"Options for '{provider_name}'"
        group = click.Group(name=provider_name, help=help)
        group.add_command(provider_notify_command_factory(p))
        for name, description in CORE_COMMANDS.items():
            callback = func_factory(p, name)
            pretty_opt = click.Option(['--pretty/--not-pretty'], help='Output a pretty version of the JSON')
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
