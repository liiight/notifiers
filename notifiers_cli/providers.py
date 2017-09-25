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


provider_commands = [
    telegram
]
