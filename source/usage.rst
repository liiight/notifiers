Usage
=====

Basic Usage
-----------

The easiest way to initialize a notifier is via the :func:`get_notifier` helper:

.. code-block:: python

    import notifiers

    pushover = notifiers.get_notifier('pushover')

Or import it directly::

    from notifiers.providers.pushover import Pushover
    pushover = Pushover()

To send a notification invoke the :func:`notify` method::

    pushover.notify(apikey='FOO', user='BAR', message='BAZ)

The :func:`notify` takes key word arguments based on the provider's schema. The ``message`` key word is used in all notifiers.

If there's a problem with sent key words, a :class:`NotifierException` will be thrown::

    import notifiers
    pushover = notifiers.get_notifier('pushover')
    pushover.notify(message='FOO')
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 215, in notify
        self._validate_data(kwargs, validator)
      File "/Users/orcarmi/PycharmProjects/notifiers/notifiers/core.py", line 193, in _validate_data
        raise BadArguments(validation_error=msg, provider=self.provider_name, data=data)
    notifiers.exceptions.BadArguments: <NotificationError: Error with sent data: 'user' is a required property>

In this case, a :class:`BadArguments` exception was thrown since not all required key words were sent.

Provider schema
---------------
Notifier's schema is constructed with `JSON Schema <http://json-schema.org/>`_. Some understanding of it is needed in order to correctly construct the notification correctly.
To see provider schema, use the ``schema`` property::

    pushover.schema
    {'type': 'object', 'properties': {'user': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}]}, 'message': {'type': 'string', 'title': 'your message'}, 'title': {'type': 'string', 'title': "your message's title, otherwise your app's name is used"}, 'token': {'type': 'string', 'title': "your application's API token"}, 'device': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': "your user's device name to send the message directly to that device"}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': "your user's device name to send the message directly to that device"}]}, 'priority': {'type': 'number', 'minimum': -2, 'maximum': 2, 'title': 'notification priority'}, 'url': {'type': 'string', 'format': 'uri', 'title': 'a supplementary URL to show with your message'}, 'url_title': {'type': 'string', 'title': 'a title for your supplementary URL, otherwise just the URL is shown'}, 'sound': {'type': 'string', 'title': "the name of one of the sounds supported by device clients to override the user's default sound choice", 'enum': ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']}, 'timestamp': {'type': 'integer', 'minimum': 0, 'title': "a Unix timestamp of your message's date and time to display to the user, rather than the time your message is received by our API"}, 'retry': {'type': 'integer', 'minimum': 30, 'title': 'how often (in seconds) the Pushover servers will send the same notification to the user. priority must be set to 2'}, 'expire': {'type': 'integer', 'maximum': 86400, 'title': 'how many seconds your notification will continue to be retried for. priority must be set to 2'}, 'callback': {'type': 'string', 'format': 'uri', 'title': 'a publicly-accessible URL that our servers will send a request to when the user has acknowledged your notification. priority must be set to 2'}, 'html': {'type': 'integer', 'minimum': 0, 'maximum': 1, 'title': 'enable HTML formatting'}}, 'additionalProperties': False, 'required': ['user', 'message', 'token']}


To see the required schema use the ``required`` property::

    pushover.required
    {'required': ['user', 'message', 'token']}

The reply is always a dict which represent the validation of the schema. In this case it's pretty straightforward, but it can be more complex at times::

    hipchat = notifiers.get_notifier('hipchat')
    hipchat.required
    {'allOf': [{'required': ['message', 'id', 'token']}, {'oneOf': [{'required': ['room']}, {'required': ['user']}], 'error_oneOf': "Only one of 'room' or 'user' is allowed"}, {'oneOf': [{'required': ['group']}, {'required': ['team_server']}], 'error_oneOf': "Only one 'group' or 'team_server' is allowed"}]}

Hipchat's validation requires `message`, `id` and `token` are sent, exactly one of of `room` or `user` and exactly one of `group` or `team_server`.

To get all of the schema properties, which correlates to the key words it can handle, use ``arguments``::

    pushover.arguments
    {'user': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': 'the user/group key (not e-mail address) of your user (or you)'}]}, 'message': {'type': 'string', 'title': 'your message'}, 'title': {'type': 'string', 'title': "your message's title, otherwise your app's name is used"}, 'token': {'type': 'string', 'title': "your application's API token"}, 'device': {'oneOf': [{'type': 'array', 'items': {'type': 'string', 'title': "your user's device name to send the message directly to that device"}, 'minItems': 1, 'uniqueItems': True}, {'type': 'string', 'title': "your user's device name to send the message directly to that device"}]}, 'priority': {'type': 'number', 'minimum': -2, 'maximum': 2, 'title': 'notification priority'}, 'url': {'type': 'string', 'format': 'uri', 'title': 'a supplementary URL to show with your message'}, 'url_title': {'type': 'string', 'title': 'a title for your supplementary URL, otherwise just the URL is shown'}, 'sound': {'type': 'string', 'title': "the name of one of the sounds supported by device clients to override the user's default sound choice", 'enum': ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']}, 'timestamp': {'type': 'integer', 'minimum': 0, 'title': "a Unix timestamp of your message's date and time to display to the user, rather than the time your message is received by our API"}, 'retry': {'type': 'integer', 'minimum': 30, 'title': 'how often (in seconds) the Pushover servers will send the same notification to the user. priority must be set to 2'}, 'expire': {'type': 'integer', 'maximum': 86400, 'title': 'how many seconds your notification will continue to be retried for. priority must be set to 2'}, 'callback': {'type': 'string', 'format': 'uri', 'title': 'a publicly-accessible URL that our servers will send a request to when the user has acknowledged your notification. priority must be set to 2'}, 'html': {'type': 'integer', 'minimum': 0, 'maximum': 1, 'title': 'enable HTML formatting'}}


