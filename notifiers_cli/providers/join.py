import click


@click.group(name='join')
def join_cmd():
    """Join specific CLI"""


@join_cmd.command(short_help='Get active devices')
@click.argument('apikey')
@click.pass_context
def devices(ctx, apikey):
    """Get a list of active devices associated with the apikey"""
    from notifiers.providers.join import Join
    devices = Join().devices(apikey)
    if not devices:
        click.echo('You have no devices associated with this apikey')
        ctx.exit()
    for device in devices:
        click.echo(f'Device name: {device["deviceName"]} - ID: {device["deviceId"]}')
