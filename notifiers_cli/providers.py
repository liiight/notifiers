"""
Provider specific commands. Some providers may need/enable commands outside of the regular notify scope
"""
from collections import defaultdict

import click


@click.group()
def telegram():
    """Telegram specific commands"""


@telegram.command()
@click.argument('token')
@click.pass_context
def updates(ctx, token):
    """Get a list of active chat IDs for your bot. If the list is empty, or you don't see a specific chat in here,
     send any message to your bot in the request chat"""
    from notifiers.providers.telegram import Telegram
    updates = Telegram().updates(token)
    if not updates:
        click.echo(f'Bot has not active chats! Send it ANY message and try again')
        ctx.exit()
    chat_ids = defaultdict(dict)
    for update in updates:
        chat_ids[update['message']['chat']['id']] = update['message']['chat']
    for chat_id, update in chat_ids.items():
        click.echo(f'Chat ID: {chat_id} - {update}')


@click.group()
def gitter():
    """Gitter specific commands"""


@gitter.command()
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


provider_commands = [
    telegram,
    gitter
]
