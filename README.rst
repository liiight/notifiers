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

See `Changelog <https://github.com/liiight/notifiers/blob/master/CHANGELOG.md>`_ for recent changes

Got an app or service and you want to enable your users to use notifications with their provider of choice? You don't need to implement a solution yourself, or use individual provider libs. A one stop shop for all notification providers with a unified and simple interface.
See below for a list of `Supported providers`_

Advantages
----------
- Spend your precious time on your own code base, instead of chasing down 3rd party provider APIs. That's what we're here for!
- With a minimal set of well known and stable dependencies (`requests <https://pypi.python.org/pypi/requests>`_, `jsonschema <https://pypi.python.org/pypi/jsonschema/2.6.0>`_ and `click <https://pypi.python.org/pypi/click/6.7>`_) you're better off than installing 3rd party SDKs.
- A unified interface means that you already support any new providers that will be added, no more work needed!
- Thorough testing means protection against any breaking API changes. We make sure your code your notifications will always get delivered!

Basic Usage
-----------

.. code:: python

    >>> from notifiers import get_notifier
    >>> p = get_notifier('pushover')
    >>> p.required
    ['user', 'message', 'token']
    >>> p.notify(user='foo', token='bar', message='test')
    <NotificationResponse,provider=Pushover,status=Success>

Setup
-----
Install with pip::

    pip install notifiers

Usage
-----

Get a notifier:

.. code:: python

    >>> import notifiers
    >>> pushover = notifiers.get_notifier('pushover')
    >>> pushover
    <NotificationProvider:[Pushover]>

Or:

.. code:: python

    >>> from notifiers.providers.pushover import Pushover
    >>> pushover = Pushover()

Send a notification:

.. code:: python

    >>> pushover.notify(token='TOKEN', title='Foo', message='Bar')

Get notifier metadata:

.. code:: python

    >>> pushover.metadata
    {'base_url': 'https://api.pushover.net/1/messages.json', 'site_url': 'https://pushover.net/', 'provider_name': 'pushover'}

Required arguments:

.. code:: python

    >>> pushover.required
    ['user', 'message', 'token']

All arguments (in JSON schema format):

.. code:: python

    >>> pushover.arguments
    {'user': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}]}, 'message': {'type': 'string', 'title': 'your message'}, 'title': {'type': 'string', 'title': "your message's title, otherwise your app's name is used"}, 'token': {'type': 'string', 'title': "your application's API token"}, 'device': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': "your user's device name to send the message directly to that device"}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': "your user's device name to send the message directly to that device"}]}, 'priority': {'oneOf': [{'type': 'number', 'minimum': -2, 'maximum': 2}, {'type': 'string'}], 'title': 'notification priority'}, 'url': {'type': 'string', 'format': 'uri', 'title': 'a supplementary URL to show with your message'}, 'url_title': {'type': 'string', 'title': 'a title for your supplementary URL, otherwise just the URL is shown'}, 'sound': {'type': 'string', 'title': "the name of one of the sounds supported by device clients to override the user's default sound choice"}, 'timestamp': {'type': 'integer', 'minimum': 0, 'title': "a Unix timestamp of your message's date and time to display to the user, rather than the time your message is received by our API"}, 'retry': {'type': 'integer', 'minimum': 30, 'title': 'how often (in seconds) the Pushover servers will send the same notification to the user. priority must be set to 2'}, 'expire': {'type': 'integer', 'maximum': 86400, 'title': 'how many seconds your notification will continue to be retried for. priority must be set to 2'}, 'callback': {'type': 'string', 'format': 'uri', 'title': 'a publicly-accessible URL that our servers will send a request to when the user has acknowledged your notification. priority must be set to 2'}, 'html': {'type': 'integer', 'minimum': 0, 'maximum': 1, 'title': 'enable HTML formatting'}}

View all available providers (continuously updated):

.. code:: python

    >>> notifiers.all_providers()
    ['pushover', 'simplepush', 'slack', 'email', 'gmail', 'pushbullet']

Some provider have default values set:

.. code:: python

    >>> e = notifiers.get_notifier('gmail')
    >>> e.defaults
    {'subject': "New email from 'notifiers'!", 'from': '<USER@LOCAL_HOST>', 'host': 'smtp.gmail.com', 'port': 587, 'tls': True, 'ssl': False, 'html': False}


Environment variables
---------------------

You can set environment variable to replace any argument that the notifier can use. The default syntax to follow is ``NOTIFIERS_[PROVIDER_NAME]_[ARGUMENT_NAME]``::

    export NOTIFIERS_PUSHOVER_TOKEN=FOO
    export NOTIFIERS_PUSHOVER_USER=BAR

Then you could just use:

.. code:: python

    >>> p.notify(message='message')

Note that you can also set ``MESSAGE`` in an environment variable.
You can also change the default prefix of ``NOTIFIERS_`` by pass the ``env_prefix`` argument on notify:

.. code:: python

    >>> p.notify(message='test', env_prefix='MY_OWN_PREFIX_')

Command Line Interface
----------------------

Notifiers come with CLI support::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers
    Usage: notifiers [OPTIONS] COMMAND [ARGS]...

      Notifiers CLI operation

    Options:
      --help  Show this message and exit.

    Commands:
      arguments  Shows the name and schema of all the...
      defaults   Shows the provider's defaults.
      metadata   Shows the provider's metadata.
      notify     Send a notification to a passed provider.
      providers  Shows all available providers
      required   Shows the required attributes of a provider.

Because of the dynamic nature of using different provider options, those are passed in a keyword=value style to the command as so::

    $ notifiers notify pushover token=foo user=bar message=test

Environment variables are used in the CLI as well. Explicitly passing keyword values takes precedence.
You can also pipe into the command::

    $ cat file.txt | notifiers notify pushover token=foo user=bar

You can set ``NOTIFIERS_DEFAULT_PROVIDER`` environment variable which will be used by the CLI. Combining that with the other required provider arguments can lead to very succinct commands::

    $ cat file.txt | notifiers notify

Note that unlike the other environment variables, you cannot change the prefix of this one.

Provider specific CLI
---------------------

Some providers have their own CLI commands::

    $ notifiers telegram --help
    Usage: core.py telegram [OPTIONS] COMMAND [ARGS]...

      Telegram specific commands

    Options:
      --help  Show this message and exit.

    Commands:
      updates  Get a list of active chat IDs for your bot.


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

In the near future
------------------

-  SendGrid, Graphite, Stride, Prowl, Teams, Twilio and many more...
-  Docs!

Why python 3 only?
~~~~~~~~~~~~~~~~~~

I wanted to avoid the whole unicode issue fiasco if possible, but
there isn't a real constraint in adding python 2 support. If there’s an
overwhelming desire for this, i’ll do it. Probably.
