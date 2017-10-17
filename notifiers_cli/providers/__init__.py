from . import gitter, telegram, pushbullet

provider_commands = [
    telegram.telegram_cmd,
    gitter.gitter_cmd,
    pushbullet.pushbullet_cmd
]