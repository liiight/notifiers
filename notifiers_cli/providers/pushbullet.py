import click


@click.group(name='pushbullet')
def pushbullet_cmd():
    """Pushbullet specific CLI"""


@pushbullet_cmd.command(short_help='Get active devices')
@click.argument('token')
@click.pass_context
def devices(ctx, token):
    """Get a list of active devices associated with the token"""
    from notifiers.providers.pushbullet import Pushbullet
    devices = Pushbullet().devices(token)
    if not devices:
        click.echo('You have no devices associated with this token')
        ctx.exit()
    for device in devices:
        if device['active']:
            click.echo(f'Nickname: {device["nickname"]} - Iden: {device["iden"]}')
