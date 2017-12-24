import click


@click.group(name='hipchat')
def hipchat_cmd():
    """Hipchat specific CLI"""


@hipchat_cmd.command(short_help='Get rooms by token')
@click.argument('token')
@click.option('-g', '--group', help="Hipchat group ID. Either this or '--team-server' are required")
@click.option('-t', '--team-server', help="Hipchat Team server. Either this or '--group' are required")
@click.option('--start', type=click.INT, help='Start index')
@click.option('--max-results', type=click.INT, help='Maximum number of results')
@click.option('--private/--no-private', help='Should private rooms be displayed', default=True)
@click.option('--archived/--no-archived', help='Should archived rooms be displayed', default=True)
@click.pass_context
def rooms(ctx, token, group, team_server, start, max_results, private, archived):
    """Get a list of rooms associated with the group or team server"""
    from notifiers.providers.hipchat import HipChat
    rooms = HipChat().rooms(token, group, team_server, start, max_results, private, archived)['items']
    if not rooms:
        click.echo('You have no rooms associated with this token')
        ctx.exit()
    for room in rooms:
        click.echo(f'Room name: {room["name"]} - ID: {room["id"]}')


@hipchat_cmd.command(short_help='Get users by token')
@click.argument('token')
@click.option('-g', '--group', help="Hipchat group ID. Either this or '--team-server' are required")
@click.option('-t', '--team-server', help="Hipchat Team server. Either this or '--group' are required")
@click.option('--start', type=click.INT, help='Start index')
@click.option('--max-results', type=click.INT, help='Maximum number of results')
@click.option('--guests/--no-guests', help='Should guest users be displayed', default=True)
@click.option('--deleted/--no-deleted', help='Should deleted users be displayed', default=True)
@click.pass_context
def users(ctx, token, group, team_server, start, max_results, guests, deleted):
    """Get a list of users associated with the group or team server"""
    from notifiers.providers.hipchat import HipChat
    users = HipChat().users(token, group, team_server, start, max_results, guests, deleted)['items']
    if not users:
        click.echo('You have no users associated with this token')
        ctx.exit()
    for user in users:
        click.echo(f'User name: {user["name"]} - ID: {user["id"]}')
