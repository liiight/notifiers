import sys
from functools import partial

import click

from notifiers import __version__, get_notifier
from notifiers.core import all_providers
from notifiers.exceptions import NotifierException
from notifiers_cli.utils.callbacks import _notify, _resource, _resources, func_factory
from notifiers_cli.utils.dynamic_click import CORE_COMMANDS, schema_to_command


def provider_group(provider_name: str) -> click.Group:
    """Builds the command group of a provider: ``notify``, its resources and the core commands"""
    p = get_notifier(provider_name, strict=True)
    group = click.Group(name=provider_name, help=f"Options for '{provider_name}'")

    # Notify command
    group.add_command(schema_to_command(p, "notify", partial(_notify, p=p), add_message=True))

    # Resources command
    group.add_command(click.Command("resources", callback=partial(_resources, p=p), help="Show provider resources list"))

    # Any provider resources
    for resource in p.resources:
        rsc = getattr(p, resource)
        rsrc_command = schema_to_command(rsc, resource, partial(_resource, rsc), add_message=False)
        rsrc_command.params.append(click.Option(["--pretty/--not-pretty"], help="Output a pretty version of the JSON"))
        group.add_command(rsrc_command)

    for name, description in CORE_COMMANDS.items():
        command = click.Command(
            name,
            callback=func_factory(p, name),
            help=description.format(provider_name),
            params=[click.Option(["--pretty/--not-pretty"], help="Output a pretty version of the JSON")],
        )
        group.add_command(command)
    return group


class NotifiersCLI(click.Group):
    """
    The main command group. Provider groups are built on demand, so running a command only builds the invoked
    provider's commands. Providers are discovered when listing commands (e.g. ``--help``)
    """

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted({*super().list_commands(ctx), *all_providers()})

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command
        if cmd_name not in all_providers():
            return None
        return provider_group(cmd_name)

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        # Listing the provider help texts doesn't need their commands built
        rows = []
        for name in self.list_commands(ctx):
            command = super().get_command(ctx, name)
            help_text = command.get_short_help_str(formatter.width) if command else f"Options for '{name}'"
            rows.append((name, help_text))
        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)


@click.group(cls=NotifiersCLI)
@click.version_option(version=__version__, prog_name="notifiers", message=("%(prog)s %(version)s"))
@click.option("--env-prefix", help="Set a custom prefix for env vars usage")
@click.pass_context
def notifiers_cli(ctx, env_prefix):
    """Notifiers CLI operation"""
    ctx.obj["env_prefix"] = env_prefix


@notifiers_cli.command()
def providers():
    """Shows all available providers"""
    click.echo(", ".join(all_providers()))


def provider_group_factory():
    """
    Adds a command group for every provider to the CLI.

    Not needed to run the CLI, which builds provider groups on demand. Useful to build all of them up front, e.g. to
    introspect the full command tree
    """
    for provider in all_providers():
        notifiers_cli.add_command(provider_group(provider))


def entry_point():
    """The entry that CLI is executed from"""
    try:
        notifiers_cli(obj={})
    except NotifierException as e:
        click.secho(f"ERROR: {e.message}", bold=True, fg="red")
        sys.exit(1)


if __name__ == "__main__":
    entry_point()
