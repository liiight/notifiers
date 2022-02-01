from . import email
from . import gitter
from . import gmail
from . import icloud
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
from . import victorops
from . import zulip

_all_providers = {
    "pushover": pushover.Pushover,
    "simplepush": simplepush.SimplePush,
    "slack": slack.Slack,
    "email": email.SMTP,
    "gmail": gmail.Gmail,
    "icloud": icloud.iCloud,
    "telegram": telegram.Telegram,
    "gitter": gitter.Gitter,
    "pushbullet": pushbullet.Pushbullet,
    "join": join.Join,
    "zulip": zulip.Zulip,
    "twilio": twilio.Twilio,
    "pagerduty": pagerduty.PagerDuty,
    "mailgun": mailgun.MailGun,
    "popcornnotify": popcornnotify.PopcornNotify,
    "statuspage": statuspage.Statuspage,
    "victorops": victorops.VictorOps,
}
