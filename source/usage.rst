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

Writing Your Own Providers
-------------------------

The notifiers package is designed to be extensible, allowing you to create and integrate your own notification providers.
This guide will walk you through the process of creating a custom provider and making it available to others.

Creating a Custom Provider
~~~~~~~~~~~~~~~~~~~~~~~~~

To create a custom provider, you need to:

1. Create a new class that inherits from ``Provider``
2. Implement the required methods and schema
3. Register your provider

Here's a basic example:

.. code:: python

    from notifiers.core import Provider, Response
    from notifiers.utils.schema import one_of
    
    class MyCustomProvider(Provider):
        name = "my_provider"
        site_url = "https://my-provider.com"
        
        # Define your provider's schema
        _required = {"required": ["message", "api_key"]}
        _schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "api_key": {"type": "string"},
                "msgtype": one_of(["text", "html"], default="text")
            },
            "additionalProperties": False
        }
        
        def _notify(self, data: dict) -> Response:
            # Implement your notification logic here
            return Response(status="Success", provider=self.name, data=data)

Making Your Provider Installable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make your provider available to others, you need to:

1. Create a proper Python package structure
2. Define an entry point in your ``setup.py``

Here's the recommended package structure:

.. code::

    myproject/
    ├── myproject/
    │   ├── __init__.py
    │   └── provider.py    # Contains your provider implementation
    ├── setup.py
    ├── README.md
    └── requirements.txt

Configure your ``setup.py`` to register the provider:

.. code:: python

    from setuptools import setup, find_packages

    setup(
        name="myproject",
        version="0.1.0",
        packages=find_packages(),
        install_requires=[
            "notifiers>=1.0.0"
        ],
        # Register your provider as an entry point
        entry_points={
            "notifiers": [
                "my_provider = myproject.provider:MyCustomProvider"
            ]
        },
        author="Your Name",
        author_email="your.email@example.com",
        description="A custom notification provider for notifiers",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        url="https://github.com/yourusername/myproject",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.6",
    )

Using Your Custom Provider
~~~~~~~~~~~~~~~~~~~~~~~~

Once installed, your provider can be used like any built-in provider:

.. code:: python

    >>> from notifiers import get_notifier
    >>> notifier = get_notifier('my_provider')
    >>> notifier.notify(
    ...     message='Hello from my custom provider!',
    ...     api_key='your-api-key'
    ... )

Testing Your Provider
~~~~~~~~~~~~~~~~~~~

It's crucial to thoroughly test your provider. Here's how to set up tests:

.. code:: python

    import pytest
    from notifiers.core import Provider
    from notifiers.exceptions import BadArguments

    def test_provider_arguments():
        provider = MyCustomProvider()
        data = {
            "message": "test message",
            "api_key": "test_key"
        }
        rsp = provider.notify(**data)
        assert rsp.status == "Success"

        # Test invalid arguments
        with pytest.raises(BadArguments):
            provider.notify(message="test")  # Missing api_key

Schema Validation
~~~~~~~~~~~~~~~

The schema is crucial for validating input parameters. Here's a detailed example:

.. code:: python

    class MyCustomProvider(Provider):
        _required = {
            "required": ["message", "api_key"],
            "dependencies": {
                "username": ["password"]  # If username is provided, password is required
            }
        }
        _schema = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "title": "Message",
                    "description": "The notification message"
                },
                "api_key": {
                    "type": "string",
                    "title": "API Key",
                    "description": "Your API authentication key"
                },
                "username": {
                    "type": "string",
                    "title": "Username",
                },
                "password": {
                    "type": "string",
                    "title": "Password",
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 10,
                    "title": "Timeout",
                    "description": "Request timeout in seconds"
                }
            },
            "additionalProperties": False
        }

Troubleshooting Guide
~~~~~~~~~~~~~~~~~~~

Common issues and solutions when developing providers:

1. **Entry Point Not Found**

   - Ensure your ``setup.py`` entry point exactly matches your provider class
   - Verify the package is installed in development mode (``pip install -e .``)
   - Check that the provider module is importable

2. **Schema Validation Errors**

   - Use the ``notify`` method's ``raise_on_errors`` parameter to debug
   - Check all required fields are provided
   - Verify data types match the schema

3. **Response Handling**

   - Always return a ``Response`` object from ``_notify``
   - Include relevant error messages in the response
   - Handle API rate limits and timeouts

Real-World Example
~~~~~~~~~~~~~~~~

Here's a complete example of a provider that sends notifications via a REST API:

.. code:: python

    import requests
    from notifiers.core import Provider, Response
    from notifiers.utils.schema import one_of
    from notifiers.exceptions import NotifierException

    class RestAPIProvider(Provider):
        name = "rest_api"
        site_url = "https://api.example.com"
        
        _required = {"required": ["message", "api_key", "endpoint"]}
        _schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "api_key": {"type": "string"},
                "endpoint": {"type": "string"},
                "method": one_of(["GET", "POST"], default="POST"),
                "timeout": {"type": "integer", "minimum": 1, "default": 10}
            }
        }
        
        def _notify(self, data: dict) -> Response:
            try:
                headers = {
                    "Authorization": f"Bearer {data['api_key']}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": data["message"]
                }
                
                response = requests.request(
                    method=data["method"],
                    url=f"{self.site_url}/{data['endpoint']}",
                    headers=headers,
                    json=payload,
                    timeout=data.get("timeout", 10)
                )
                
                response.raise_for_status()
                
                return Response(
                    status="Success",
                    provider=self.name,
                    data=response.json()
                )
                
            except requests.exceptions.RequestException as e:
                raise NotifierException(
                    provider=self.name,
                    message=f"API request failed: {str(e)}"
                )

Usage example:

.. code:: python

    >>> notifier = get_notifier('rest_api')
    >>> notifier.notify(
    ...     message="Hello API",
    ...     api_key="your-api-key",
    ...     endpoint="notifications/send"
    ... )

Community Providers
~~~~~~~~~~~~~~~~

Here are some community-created providers that you can use or reference when building your own:

- `notifiers-wecom-provider <https://github.com/loonghao/notifiers_wecom_provider>`_: A provider for sending notifications to WeCom (企业微信)

These providers serve as excellent examples of how to implement custom notification providers. Feel free to:

- Use them directly in your projects
- Study their implementation for best practices
- Contribute to their development
- Use them as templates for your own providers

If you've created a provider, please let us know so we can add it to this list!

Best Practices
~~~~~~~~~~~~

1. Always validate input data using the schema
2. Implement proper error handling
3. Include comprehensive documentation
4. Add tests for your provider
5. Follow the notifiers package conventions

For more examples and detailed API documentation, refer to the :ref:`api_reference` section.

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
