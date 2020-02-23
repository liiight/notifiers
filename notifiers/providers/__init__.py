# flake8: noqa
from . import email
from . import gitter
from . import gmail
from . import hipchat
from . import join
from . import mailgun
from . import pagerduty
from . import popcornnotify
from . import pushbullet
from . import pushover
from . import simplepush
from . import slack
from . import statuspage
from . import telegram
from . import twilio
from . import zulip

_all_providers = {
    # "pushover": pushover.Pushover,
    # "simplepush": simplepush.SimplePush,
    # "slack": slack.Slack,
    "email": email.SMTP,
    "gmail": gmail.Gmail,
    # "telegram": telegram.Telegram,
    # "gitter": gitter.Gitter,
    # "pushbullet": pushbullet.Pushbullet,
    # "join": join.Join,
    # "hipchat": hipchat.HipChat,
    # "zulip": zulip.Zulip,
    # "twilio": twilio.Twilio,
    # "pagerduty": pagerduty.PagerDuty,
    # "mailgun": mailgun.MailGun,
    # "popcornnotify": popcornnotify.PopcornNotify,
    # "statuspage": statuspage.Statuspage,
}
