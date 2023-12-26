![Full logo](https://raw.githubusercontent.com/liiight/notifiers/main/assets/images/circle_full_logo.png)

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fnotifiers%2Fnotifiers%2Fbadge%3Fref%3Dmain&style=flat-square)](https://actions-badge.atrox.dev/notifiers/notifiers/goto?ref=master) [![Codecov](https://img.shields.io/codecov/c/github/notifiers/notifiers/master.svg?style=flat-square) ](https://codecov.io/gh/notifiers/notifiers) [![image](https://img.shields.io/gitter/room/nwjs/nw.js.svg?style=flat-square) ](https://gitter.im/notifiers/notifiers) [![PyPi version](https://img.shields.io/pypi/v/notifiers.svg?style=flat-square) ](https://pypi.python.org/pypi/notifiers) [![Supported Python versions](https://img.shields.io/pypi/pyversions/notifiers.svg?style=flat-square) ](https://pypi.org/project/notifiers) [![License](https://img.shields.io/pypi/l/notifiers.svg?style=flat-square) ](https://choosealicense.com/licenses) [![Status](https://img.shields.io/pypi/status/notifiers.svg?style=flat-square) ](https://pypi.org/project/notifiers/) [![Docker build](https://img.shields.io/docker/cloud/build/liiight/notifiers?style=flat-square) ](https://hub.docker.com/r/liiight/notifiers/) [![RTD](https://img.shields.io/readthedocs/notifiers.svg?style=flat-square) ](https://readthedocs.org/projects/notifiers/badge/?version=latest) [![Paypal](https://img.shields.io/badge/Donate-PayPal-green.svg?style=flat-square) ](https://paypal.me/notifiers) [![Downloads](http://pepy.tech/badge/notifiers)](http://pepy.tech/count/notifiers)
[![Twitter Follow](https://img.shields.io/twitter/follow/liiight.svg?style=flat-square&logo=twitter&label=Follow)](https://twitter.com/liiight) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


See [changelog](http://notifiers.readthedocs.io/en/latest/changelog.html) for recent changes

Got an app or service, and you want to enable your users to use notifications with their provider of choice? Working on a script and you want to receive notification based on its output? You don't need to implement a solution yourself, or use individual provider libs. A one stop shop for all notification providers with a unified and simple interface.

# Supported providers


[Pushover](https://pushover.net/), [SimplePush](https://simplepush.io/), [Slack](https://api.slack.com/), [Gmail](https://www.google.com/gmail/about/), Email (SMTP), [Telegram](https://telegram.org/), [Gitter](https://gitter.im), [Pushbullet](https://www.pushbullet.com), [Join](https://joaoapps.com/join/), [Zulip](https://zulipchat.com/), [Twilio](https://www.twilio.com/), [Pagerduty](https://www.pagerduty.com), [Mailgun](https://www.mailgun.com/), [PopcornNotify](https://popcornnotify.com), [StatusPage.io](https://statuspage.io), [iCloud](https://www.icloud.com/mail), [VictorOps (Splunk)](https://www.splunk.com/en_us/investor-relations/acquisitions/splunk-on-call.html), [Notify](https://github.com/K0IN/Notify)

# Advantages

-   Spend your precious time on your own code base, instead of chasing down 3rd party provider APIs. That's what we're here for!
-   With a minimal set of well known and stable dependencies ([requests](https://pypi.python.org/pypi/requests), [jsonschema](https://pypi.python.org/pypi/jsonschema/2.6.0) and [click](https://pypi.python.org/pypi/click/6.7)) you're better off than installing 3rd party SDKs.
-   A unified interface means that you already support any new providers that will be added, no more work needed!
-   Thorough testing means protection against any breaking API changes. We make sure your code your notifications will always get delivered!

# Installation

Via pip:
```
$ pip install notifiers
```
Via homebrew:
```
$ brew install notifiers
```
Or Dockerhub:
```
$ docker pull liiight/notifiers
```
# Basic Usage

```python
>>> from notifiers import get_notifier
>>> p = get_notifier('pushover')
>>> p.required
{'required': ['user', 'message', 'token']}
>>> p.notify(user='foo', token='bar', message='test')
<NotificationResponse,provider=Pushover,status=Success>
```

Or:
```python
>>> from notifiers import notify
>>> notify('pushover', user='foo', token='bar', message='test')
<NotificationResponse,provider=Pushover,status=Success>
```

# From CLI

```text
$ notifiers pushover notify --user foo --token baz "This is so easy!"
```

# As a logger

Directly add to your existing stdlib logging:

```python
>>> import logging
>>> from notifiers.logging import NotificationHandler

>>> log = logging.getLogger(__name__)

>>> defaults = {
        'token': 'foo',
        'user': 'bar'
    }
>>> hdlr = NotificationHandler('pushover', defaults=defaults)
>>> hdlr.setLevel(logging.ERROR)

>>> log.addHandler(hdlr)
>>> log.error('And just like that, you get notified about all your errors!')
```

# Mentions

- Mentioned in [Python Bytes](https://pythonbytes.fm/episodes/show/67/result-of-moving-python-to-github) podcast

# Road map

-   Many more providers!
-   Low level providers (Amazon SNS, Google FCM, OS Toast messages) via `extra` dependencies

See [Docs](http://notifiers.readthedocs.io/) for more information

# Donations

If you like this and want to buy me a cup of coffee, please click the donation button above or click this [link](https://paypal.me/notifiers) ☕

# Code of Conduct

Everyone interacting in the Notifiers project's codebases, issue trackers and chat rooms is expected to follow the [PyPA Code of Conduct.](https://www.pypa.io/en/latest/code-of-conduct/)
