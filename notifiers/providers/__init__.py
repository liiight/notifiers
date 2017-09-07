from . import pushover, simplepush, slack

_all_providers = {
    'pushover': pushover.Pushover,
    'simplepush': simplepush.SimplePush,
    'slack': slack.Slack
}
