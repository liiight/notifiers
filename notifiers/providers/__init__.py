from . import pushover, simplepush, slack, email, gmail, telegram, gitter

_all_providers = {
    'pushover': pushover.Pushover,
    'simplepush': simplepush.SimplePush,
    'slack': slack.Slack,
    'email': email.SMTP,
    'gmail': gmail.Gmail,
    'telegram': telegram.Telegram,
    'gitter': gitter.Gitter
}
