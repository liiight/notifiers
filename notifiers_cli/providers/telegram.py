from collections import defaultdict

import click


@click.group(name='telegram')
def telegram_cmd():
    """Telegram specific commands"""


@telegram_cmd.command(short_help='Active chat IDs')
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