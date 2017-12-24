from . import pushover, simplepush, slack, email, gmail, telegram, gitter, pushbullet, join, hipchat

_all_providers = {
    'pushover': pushover.Pushover,
    'simplepush': simplepush.SimplePush,
    'slack': slack.Slack,
    'email': email.SMTP,
    'gmail': gmail.Gmail,
    'telegram': telegram.Telegram,
    'gitter': gitter.Gitter,
    'pushbullet': pushbullet.Pushbullet,
    'join': join.Join,
    'hipchat': hipchat.HipChat
}
