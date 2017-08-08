Notifiers
=========

.. image:: https://img.shields.io/travis/liiight/notifiers/master.svg
    :target: https://travis-ci.org/liiight/notifiers

.. image:: https://codecov.io/gh/liiight/notifiers/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/liiight/notifiers

.. image:: https://img.shields.io/gitter/room/nwjs/nw.js.svg
    :target: https://gitter.im/notifiers/notifiers

The easiest way to send push notifications! Got an app or service and you want to enable your users to use push notification with their provider of choice? You don't need to implement solution yourself, or use individual provider libs. A one stop shop for all notification providers with a unified and simple interface.


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
    ['pushover']


In the near future
------------------

-  Many more providers
-  CLI support
-  Environment variable support
-  Docs

Why python 3 only?
~~~~~~~~~~~~~~~~~~

I wanted to avoid the whole unicode issue fiasco if possible, but
there’s not real constraint in adding python 2 support. If there’s an
overwhelming desire for this, i’ll do it. Probably.

