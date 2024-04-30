Usage
=====

Basic Usage
-----------

The easiest way to initialize a notifier is via the :func:`~notifiers.core.get_notifier` helper:

.. code-block:: python

    >>> import notifiers
    >>> pushover = notifiers.get_notifier('pushover')

Or import it directly:

.. code-block:: python

    >>> from notifiers.providers.pushover import Pushover
    >>> pushover = Pushover()

To send a notification invoke the :meth:`~notifiers.core.Provider.notify` method:

    >>> pushover.notify(apikey='FOO', user='BAR', message='BAZ')

The :meth:`notifiers.core.Provider.notify` method takes key word arguments based on the provider's schema. The ``message`` key word is used in all notifiers.

.. note::

    You can also send a notification without getting a provider object via the :meth:`notifiers.core.notify` method:

    .. code-block:: python

        >>> from notifiers import notify
        >>> notify('pushover', apikey='FOO', user='BAR', message='BAZ').

    The first argument of the :meth:`~notifiers.core.notify` method is the requested provider name. If such does not exist a :class:`~notifiers.exception.NoSuchNotifierError` exception will be raised.

    If there's a problem with sent key words, a :class:`~notifiers.exceptions.NotifierException` will be thrown:

.. code-block:: python

    >>> import notifiers
    >>> pushover = notifiers.get_notifier('pushover')
    >>> pushover.notify(message='FOO')
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "/Users/liiight/PycharmProjects/notifiers/notifiers/core.py", line 215, in notify
        self._validate_data(kwargs, validator)
      File "/Users/liiight/PycharmProjects/notifiers/notifiers/core.py", line 193, in _validate_data
        raise BadArguments(validation_error=msg, provider=self.name, data=data)
    notifiers.exceptions.BadArguments: <NotificationError: Error with sent data: 'user' is a required property>

In this case, a :class:`~notifiers.exceptions.BadArguments` exception was thrown since not all required key words were sent.

Provider schema
---------------
Notifier's schema is constructed with `JSON Schema <http://json-schema.org/>`_. Some understanding of it is needed in order to correctly construct the notification correctly.
To see provider schema, use the ``schema`` property:

    >>> pushover.schema
    {'type': 'object', 'properties': {'user': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}]}, 'message': {'type': 'string', 'title': 'your message'}, 'title': {'type': 'string', 'title': "your message's title, otherwise your app's name is used"}, 'token': {'type': 'string', 'title': "your application's API token"}, 'device': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': "your user's device name to send the message directly to that device"}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': "your user's device name to send the message directly to that device"}]}, 'priority': {'type': 'number', 'minimum': -2, 'maximum': 2, 'title': 'notification priority'}, 'url': {'type': 'string', 'format': 'uri', 'title': 'a supplementary URL to show with your message'}, 'url_title': {'type': 'string', 'title': 'a title for your supplementary URL, otherwise just the URL is shown'}, 'sound': {'type': 'string', 'title': "the name of one of the sounds supported by device clients to override the user's default sound choice", 'enum': ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']}, 'timestamp': {'type': 'integer', 'minimum': 0, 'title': "a Unix timestamp of your message's date and time to display to the user, rather than the time your message is received by our API"}, 'retry': {'type': 'integer', 'minimum': 30, 'title': 'how often (in seconds) the Pushover servers will send the same notification to the user. priority must be set to 2'}, 'expire': {'type': 'integer', 'maximum': 86400, 'title': 'how many seconds your notification will continue to be retried for. priority must be set to 2'}, 'callback': {'type': 'string', 'format': 'uri', 'title': 'a publicly-accessible URL that our servers will send a request to when the user has acknowledged your notification. priority must be set to 2'}, 'html': {'type': 'integer', 'minimum': 0, 'maximum': 1, 'title': 'enable HTML formatting'}}, 'additionalProperties': False, 'required': ['user', 'message', 'token']}


To see the required schema use the ``required`` property:

    >>> pushover.required
    {'required': ['user', 'message', 'token']}

The reply is always a dict which represent the validation of the schema. In this case it's pretty straightforward, but it can be more complex at times:

    >>> hipchat = notifiers.get_notifier('hipchat')
    >>> hipchat.required
    {'allOf': [{'required': ['message', 'id', 'token']}, {'oneOf': [{'required': ['room']}, {'required': ['user']}], 'error_oneOf': "Only one of 'room' or 'user' is allowed"}, {'oneOf': [{'required': ['group']}, {'required': ['team_server']}], 'error_oneOf': "Only one 'group' or 'team_server' is allowed"}]}

Hipchat's validation requires ``message``, ``id`` and ``token`` are sent, exactly one of of ``room`` or ``user`` and exactly one of ``group`` or ``team_server``.

To get all of the schema properties, which correlates to the key words it can handle, use ``arguments``:

    >>> pushover.arguments
    {'user': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}]}, 'message': {'type': 'string', 'title': 'your message'}, 'title': {'type': 'string', 'title': "your message's title, otherwise your app's name is used"}, 'token': {'type': 'string', 'title': "your application's API token"}, 'device': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': "your user's device name to send the message directly to that device"}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': "your user's device name to send the message directly to that device"}]}, 'priority': {'type': 'number', 'minimum': -2, 'maximum': 2, 'title': 'notification priority'}, 'url': {'type': 'string', 'format': 'uri', 'title': 'a supplementary URL to show with your message'}, 'url_title': {'type': 'string', 'title': 'a title for your supplementary URL, otherwise just the URL is shown'}, 'sound': {'type': 'string', 'title': "the name of one of the sounds supported by device clients to override the user's default sound choice", 'enum': ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']}, 'timestamp': {'type': 'integer', 'minimum': 0, 'title': "a Unix timestamp of your message's date and time to display to the user, rather than the time your message is received by our API"}, 'retry': {'type': 'integer', 'minimum': 30, 'title': 'how often (in seconds) the Pushover servers will send the same notification to the user. priority must be set to 2'}, 'expire': {'type': 'integer', 'maximum': 86400, 'title': 'how many seconds your notification will continue to be retried for. priority must be set to 2'}, 'callback': {'type': 'string', 'format': 'uri', 'title': 'a publicly-accessible URL that our servers will send a request to when the user has acknowledged your notification. priority must be set to 2'}, 'html': {'type': 'integer', 'minimum': 0, 'maximum': 1, 'title': 'enable HTML formatting'}}

.. _environs:

Environment variables
---------------------
You can set environment variable to replace any argument that the notifier can use. The default syntax to follow is ``NOTIFIERS_[PROVIDER_NAME]_[ARGUMENT_NAME]``:

.. code-block:: console

    $ export NOTIFIERS_PUSHOVER_TOKEN=FOO
    $ export NOTIFIERS_PUSHOVER_USER=BAR

Then you could just use:

.. code:: python

    >>> p.notify(message='message')

Note that you can also set ``MESSAGE`` in an environment variable.
You can also change the default prefix of ``NOTIFIERS_`` by pass the ``env_prefix`` argument on notify:

.. code:: python

    >>> p.notify(message='test', env_prefix='MY_OWN_PREFIX_')


Provider resources
------------------

Some provider have helper method to enable fetching relevant resources (like rooms, users etc.)
To get a list of provider resources use the :meth:`notifiers.core.Provider.resources` property:

    >>> telegram.resources
    ['updates']

Resource share almost all of their functionality with the :class:`~notifiers.core.Provider` class, as they have a schema as well:

    >>> telegram.updates
    <ProviderResource,provider=telegram,resource=updates>
    >>> telegram.updates.schema
    {'type': 'object', 'properties': {'token': {'type': 'string', 'title': 'Bot token'}}, 'additionalProperties': False, 'required': ['token']}

To invoke the resource, just call it:

    >>> telegram.updates()
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 278, in __call__
        data = self._process_data(**kwargs)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 204, in _process_data
        self._validate_data(data, validator)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 175, in _validate_data
        raise BadArguments(validation_error=msg, provider=self.name, data=data)
    notifiers.exceptions.BadArguments: Error with sent data: 'token' is a required property

Oops, forgot to send ``token``. Let's try again:

    >>> telegram.updates(token='foo')
    [{'update_id': REDACTED, 'message': {'message_id': REDACTED, 'from': {'id': REDACTED, 'is_bot': False, 'first_name': 'REDACTED', 'last_name': 'REDACTED', 'username': 'REDACTED', 'language_code': 'en-US'}, 'chat': {'id': REDACTED, 'first_name': 'REDACTED', 'last_name': 'REDACTED', 'username': 'REDACTED', 'type': 'private'}, 'date': 1516178366, 'text': 'Ccc'}}]

As can be expected, each provider resource returns a completely different response that correlates to the underlying API command it wraps. In this example, by invoking the :meth:`notifiers.providers.telegram.Telegram.updates` method, you get a response that shows you which active chat IDs your telegram bot token can send to.


Handling errors
---------------
There are two base types of errors in Notifiers, data (or schema) related errors and notification related errors.
The former can present as so:

    >>> import notifiers
    >>> pushover = notifiers.get_notifier('pushover')
    >>> pushover.notify(message='FOO')
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "/Users/liiight/PycharmProjects/notifiers/notifiers/core.py", line 215, in notify
        self._validate_data(kwargs, validator)
      File "/Users/liiight/PycharmProjects/notifiers/notifiers/core.py", line 193, in _validate_data
        raise BadArguments(validation_error=msg, provider=self.name, data=data)
    notifiers.exceptions.BadArguments: <NotificationError: Error with sent data: 'user' is a required property>

Here we see that an :class:`BadArguments` exception was raised instantly, since not all required values were sent.
Another example:

    >>> pushover.notify(message='FOO', token='TOKEN', user='USER', attachment='/foo')
    Traceback (most recent call last):
      File "/Users/orcarmi/PycharmProjects/notifiers/poc.py", line 50, in <module>
        raise_on_errors=True)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 273, in notify
        data = self._process_data(**kwargs)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 203, in _process_data
        self._validate_data(data)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 176, in _validate_data
        raise BadArguments(validation_error=msg, provider=self.name, data=data)
    notifiers.exceptions.BadArguments: Error with sent data: 'foo' is not a 'valid_file'

Some values have both ``type`` and ``format`` set in their schema, which enforces a specific logic. Here we can see that the schema for pushover's ``attachment`` attribute has ``format`` set to ``valid_file`` which check that the file is present.

There are also notification based errors:
    >>> rsp = pushover.notify(message='FOO', token='BAD TOKEN', user='USER')
    >>> rsp.raise_on_errors()
    Traceback (most recent call last):
      File "/Users/orcarmi/PycharmProjects/notifiers/poc.py", line 49, in <module>
        raise_on_errors=True)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 276, in notify
        rsp.raise_on_errors()
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 48, in raise_on_errors
        raise NotificationError(provider=self.provider, data=self.data, errors=self.errors, response=self.response)
    notifiers.exceptions.NotificationError: Notification errors: application token is invalid

Note the default behaviour for :class:`~notifiers.core.Response` is not to raise exception on error. You can either use the :func:`~notifiers.core.Response.raise_on_errors()` method, or pass ``raise_on_errors=True`` to the notification command:

    >>> pushover.notify(message='FOO', token='BAD TOKEN', user='USER', raise_on_errors=True)
    Traceback (most recent call last):
      File "/Users/orcarmi/PycharmProjects/notifiers/poc.py", line 49, in <module>
        raise_on_errors=True)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 276, in notify
        rsp.raise_on_errors()
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 48, in raise_on_errors
        raise NotificationError(provider=self.provider, data=self.data, errors=self.errors, response=self.response)
    notifiers.exceptions.NotificationError: Notification errors: application token is invalid

You can also use the ``ok`` property:

    >>> rsp = pushover.notify(message='FOO', token='BAD TOKEN', user='USER')
    >>> rsp.ok
    False
    >>> rsp.errors
    ['application token is invalid']


Writing your own providers
-----------------
Making your provider installable by others
If you want to make your provider externally available,
you may define a so-called entry point for your distribution so that notifiers finds your provider module.
Entry points are a feature that is provided by Documentation.
notifiers looks up the `notifiers` entrypoint to discover its providers and you can thus make your provider available
by defining it in your setuptools-invocation:

.. code:: python

    >>> # sample ./setup.py file
    >>> from setuptools import setup

    >>> setup(
    >>>    name="myproject",
    >>>    packages=["myproject"],
    >>>    # the following makes a plugin available to notifiers
    >>>    entry_points={"notifiers": ["name_of_provider = myproject.provider"]},
    >>> )

If a package is installed this way, `notifiers` will load `myproject.provider` as a provider for notifiers.

.. code:: python

    >>> from notifiers import get_notifier
    >>> notifier = get_notifier('name_of_provider')
    >>> notifier.notify(msgtype='text', api_key='1234', message='test')

