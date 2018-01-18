Notifiers
=========
The easiest way to send notifications!

.. image:: https://img.shields.io/travis/liiight/notifiers/master.svg?style=flat-square
    :target: https://travis-ci.org/liiight/notifiers
    :alt: Travis CI

.. image:: https://img.shields.io/codecov/c/github/liiight/notifiers/master.svg?style=flat-square
    :target: https://codecov.io/gh/liiight/notifiers
    :alt: Codecov

.. image:: https://img.shields.io/gitter/room/nwjs/nw.js.svg?style=flat-square
    :target: https://gitter.im/notifiers/notifiers

.. image:: https://img.shields.io/pypi/v/notifiers.svg?style=flat-square
    :target: https://pypi.python.org/pypi/notifiers
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/notifiers.svg?style=flat-square
    :target: https://pypi.org/project/notifiers
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/notifiers.svg?style=flat-square
    :target: https://choosealicense.com/licenses
    :alt: License

.. image:: https://img.shields.io/pypi/status/notifiers.svg?style=flat-square
    :target: https://pypi.python.org/pypi/notifiers
    :alt: Status

.. image:: https://img.shields.io/docker/build/liiight/notifiers.svg?style=flat-square
    :target: https://hub.docker.com/r/liiight/notifiers/
    :alt: Docker build

.. image:: https://img.shields.io/readthedocs/notifiers.svg?style=flat-square
    :target: https://readthedocs.org/projects/notifiers/badge/?version=latest
    :alt: RTD

See `Releases <https://github.com/liiight/notifiers/releases>`_ for recent changes

.. inclusion-start

Got an app or service and you want to enable your users to use notifications with their provider of choice? Working on a script and you want to receive notification based on its output? You don't need to implement a solution yourself, or use individual provider libs. A one stop shop for all notification providers with a unified and simple interface.

Supported providers
-------------------

- `Pushover <https://pushover.net/>`_
- `SimplePush <https://simplepush.io/>`_
- `Slack <https://api.slack.com/>`_
- `Gmail <https://www.google.com/gmail/about/>`_
- Email (SMTP)
- `Telegram <https://telegram.org/>`_
- `Gitter <https://gitter.im>`_
- `Pushbullet <https://www.pushbullet.com>`_
- `Join <https://joaoapps.com/join/>`_
- `Hipchat <https://www.hipchat.com/docs/apiv2>`_
- `Zulip <https://zulipchat.com/>`_

Advantages
----------
- Spend your precious time on your own code base, instead of chasing down 3rd party provider APIs. That's what we're here for!
- With a minimal set of well known and stable dependencies (`requests <https://pypi.python.org/pypi/requests>`_, `jsonschema <https://pypi.python.org/pypi/jsonschema/2.6.0>`_ and `click <https://pypi.python.org/pypi/click/6.7>`_) you're better off than installing 3rd party SDKs.
- A unified interface means that you already support any new providers that will be added, no more work needed!
- Thorough testing means protection against any breaking API changes. We make sure your code your notifications will always get delivered!

Installation
------------
Via pip::

    pip install notifiers

Or Dockerhub::

    docker pull liiight/notifiers


Basic Usage
-----------

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> p = get_notifier('pushover')
    >>> p.required
    {'required': ['user', 'message', 'token']}
    >>> p.notify(user='foo', token='bar', message='test')
    <NotificationResponse,provider=Pushover,status=Success>

From CLI
--------

.. code-block:: console

    $ notifiers pushover notify --user foo --token baz "This is so easy!"

In the near future
------------------

-  SendGrid, Graphite, Stride, Prowl, Teams, Twilio and many more...
-  Low level providers (Amazon SNS, Google FCM, OS Toast messages) via ``extra`` dependencies
-  Docs!

Why python 3 only?
~~~~~~~~~~~~~~~~~~

I wanted to avoid the whole unicode issue fiasco if possible, but
there isn't a real constraint in adding python 2 support. If there’s an
overwhelming desire for this, i’ll do it. Probably.

.. inclusion-end

See `Docs <http://notifiers.readthedocs.io/>`_ for more information