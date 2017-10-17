import click


@click.group(name='gitter')
def gitter_cmd():
    """Gitter specific commands"""


@gitter_cmd.command(short_help='Get available rooms')
@click.argument('token')
@click.option('-q', '--query', help='Search query to be used to filter results')
@click.pass_context
def rooms(ctx, token, query):
    """Get a list of available rooms to send a notification to. This include private chats as well, as they are
    considered a room as well"""
    from notifiers.providers.gitter import Gitter
    rooms = Gitter().rooms(token, query)
    if not rooms:
        click.echo('You have no active room available')
        ctx.exit()
    for room in rooms:
        click.echo(f'Room ID: {room["id"]} - Name: {room["name"]}')
