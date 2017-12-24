from . import gitter, telegram, pushbullet, join, hipchat

provider_commands = [
    telegram.telegram_cmd,
    gitter.gitter_cmd,
    pushbullet.pushbullet_cmd,
    join.join_cmd,
    hipchat.hipchat_cmd

]