from . import gitter, telegram, pushbullet, join

provider_commands = [
    telegram.telegram_cmd,
    gitter.gitter_cmd,
    pushbullet.pushbullet_cmd,
    join.join_cmd
]