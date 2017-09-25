from . import pushover, simplepush, slack, email, gmail

_all_providers = {
    'pushover': pushover.Pushover,
    'simplepush': simplepush.SimplePush,
    'slack': slack.Slack,
    'email': email.SMTP,
    'gmail': gmail.Gmail
}
