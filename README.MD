Notifiers
=========

The easiest way to send notifications!

[![Travis CI](https://img.shields.io/travis/liiight/notifiers/master.svg?style=flat-square)](https://travis-ci.org/liiight/notifiers)[![Codecov](https://img.shields.io/codecov/c/github/liiight/notifiers/master.svg?style=flat-square)](https://codecov.io/gh/liiight/notifiers)[![image](https://img.shields.io/gitter/room/nwjs/nw.js.svg?style=flat-square)](https://gitter.im/notifiers/notifiers)[![PyPi version](https://img.shields.io/pypi/v/notifiers.svg?style=flat-square)](https://pypi.python.org/pypi/notifiers)[![Supported Python versions](https://img.shields.io/pypi/pyversions/notifiers.svg?style=flat-square)](https://pypi.org/project/notifiers)[![License](https://img.shields.io/pypi/l/notifiers.svg?style=flat-square)](https://choosealicense.com/licenses)[![Status](https://img.shields.io/pypi/status/notifiers.svg?style=flat-square)](https://pypi.python.org/pypi/notifiers)[![Docker build](https://img.shields.io/docker/build/liiight/notifiers.svg?style=flat-square)](https://hub.docker.com/r/liiight/notifiers/)[![RTD](https://img.shields.io/readthedocs/notifiers.svg?style=flat-square)](https://readthedocs.org/projects/notifiers/badge/?version=latest)

See [Releases](https://github.com/liiight/notifiers/releases) for recent
changes

Got an app or service and you want to enable your users to use
notifications with their provider of choice? Working on a script and you
want to receive notification based on its output? You don\'t need to
implement a solution yourself, or use individual provider libs. A one
stop shop for all notification providers with a unified and simple
interface.

Supported providers
-------------------

-   [Pushover](https://pushover.net/)
-   [SimplePush](https://simplepush.io/)
-   [Slack](https://api.slack.com/)
-   [Gmail](https://www.google.com/gmail/about/)
-   Email (SMTP)
-   [Telegram](https://telegram.org/)
-   [Gitter](https://gitter.im)
-   [Pushbullet](https://www.pushbullet.com)
-   [Join](https://joaoapps.com/join/)
-   [Hipchat](https://www.hipchat.com/docs/apiv2)
-   [Zulip](https://zulipchat.com/)

Advantages
----------

-   Spend your precious time on your own code base, instead of chasing down 3rd party provider APIs. That\'s what we\'re here for!
-   With a minimal set of well known and stable dependencies ([requests](https://pypi.python.org/pypi/requests), [jsonschema](https://pypi.python.org/pypi/jsonschema/2.6.0) and [click](https://pypi.python.org/pypi/click/6.7)) you\'re better off
    than installing 3rd party SDKs.
-   A unified interface means that you already support any new providers that will be added, no more work needed!
-   Thorough testing means protection against any breaking API changes. We make sure your code your notifications will always get delivered!

Installation
------------

Via pip:

    pip install notifiers

Or Dockerhub:

    docker pull liiight/notifiers

Basic Usage
-----------

```
>>> from notifiers import get_notifier
>>> p = get_notifier('pushover')
>>> p.required
{'required': ['user', 'message', 'token']}
>>> p.notify(user='foo', token='bar', message='test')
<NotificationResponse,provider=Pushover,status=Success>
```

In the near future 
------------------

-   SendGrid, Graphite, Stride, Prowl, Teams, Twilio and many more\...
-   Low level providers (Amazon SNS, Google FCM, OS Toast messages) via `extra` dependencies
-   Docs!

### Why python 3 only?

I wanted to avoid the whole unicode issue fiasco if possible, but there isn't a real constraint in adding python 2 support. If there's an
overwhelming desire for this, i'll do it. Probably.

See [Docs](http://notifiers.readthedocs.io/) for more information
