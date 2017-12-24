import click

from notifiers.core import all_providers, get_notifier
from notifiers.exceptions import NotifierException


@click.group()
def notifiers():
    """Notifiers CLI operation"""


@notifiers.command()
def providers():
    """Shows all available providers"""
    click.echo(', '.join(all_providers()))


@notifiers.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument('provider', type=click.Choice(all_providers()), envvar='NOTIFIERS_DEFAULT_PROVIDER')
@click.pass_context
def notify(ctx, provider):
    """Send a notification to a passed provider.

    Data should be passed via a key=value input like so:

        notifiers notify pushover token=foo user=bar message=test

    """
    p = get_notifier(provider)
    data = {}
    for item in ctx.args:
        data.update([item.split('=')])
    if 'message' not in data:
        message = click.get_text_stream('stdin').read()
        if not message:
            raise click.ClickException(
                "'message' option is required. "
                "Either pass it explicitly or pipe into the command"
            )
        data['message'] = message

    rsp = p.notify(**data)
    rsp.raise_on_errors()


@notifiers.command()
@click.argument('provider', type=click.Choice(all_providers()), envvar='NOTIFIERS_DEFAULT_PROVIDER')
def required(provider):
    """Shows the required attributes of a provider.
    Example:
        notifiers required pushover
    """
    p = get_notifier(provider)
    click.echo(', '.join(p.required))


@notifiers.command()
@click.argument('provider', type=click.Choice(all_providers()), envvar='NOTIFIERS_DEFAULT_PROVIDER')
def arguments(provider):
    """Shows the name and schema of all the  attributes of a provider.
    Example:

        notifiers arguments pushover
    """
    p = get_notifier(provider)
    for name, schema in p.arguments.items():
        click.echo(f"Name: '{name}', Schema: {schema}")
    click.echo(', '.join(p.required))


@notifiers.command()
@click.argument('provider', type=click.Choice(all_providers()))
def metadata(provider):
    """Shows the provider's metadata.
    Example:
        notifiers metadata pushover
    """
    p = get_notifier(provider)
    for k, v in p.metadata.items():
        click.echo(f'{k}: {v}')


@notifiers.command()
@click.argument('provider', type=click.Choice(all_providers()))
def defaults(provider):
    """Shows the provider's defaults.
    Example:
        notifiers defaults pushover
    """
    p = get_notifier(provider)
    if not p.defaults:
        click.echo(f'{provider} has no defaults set')
    for k, v in p.defaults.items():
        click.echo(f'{k}: {v}')


def entry_point():
    try:
        from notifiers_cli.providers import provider_commands
        for command in provider_commands:
            notifiers.add_command(command)
        notifiers(obj={})
    except NotifierException as e:
        click.secho(f'ERROR: {e.message}', bold=True, fg='red')
        exit(1)


if __name__ == '__main__':
    entry_point()
