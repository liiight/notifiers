import click


@click.group(name='hipchat')
def hipchat_cmd():
    """Hipchat specific CLI"""


@hipchat_cmd.command(short_help='Get room by token')
@click.argument('token')
@click.option('-g', '--group', help='Hipchat group ID. Either this or \'--team-server\' are required')
@click.option('-t', '--team-server', help='Hipchat Team server. Either this or \'--group\' are required')
@click.option('--start', type=click.INT, help='Start index')
@click.option('--max-results', type=click.INT, help='Maximum number of results')
@click.option('--private/--no-private', help='Should private rooms be displayed', default=True)
@click.option('--archived/--no-archived', help='Should archived rooms be displayed', default=True)
@click.pass_context
def room(ctx, token, group, team_server, start, max_results, private, archived):
    """Get a list of active room associated with the group or team server"""
    from notifiers.providers.hipchat import HipChat
    rooms = HipChat().rooms(token, group, team_server, start, max_results, private, archived)['items']
    if not rooms:
        click.echo('You have no room  associated with this apikey')
        ctx.exit()
    for room in rooms:
        click.echo(f'Room name: {room["name"]} - ID: {room["id"]}')
