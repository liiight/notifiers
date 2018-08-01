Email (SMTP)
------------
Enables sending email messages to SMTP servers.

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> email = get_notifier('email')
    >>> email.required
    {'required': ['message', 'to']}

    >>> email.notify(to='email@addrees.foo', message='hi!')


It uses several defaults:

.. code-block:: python

    >>> email.defaults
    {'subject': "New email from 'notifiers'!", 'from': '[USER@HOSTNAME]', 'host': 'localhost', 'port': 25, 'tls': False, 'ssl': False, 'html': False}

Any of these can be overridden by sending them to the :func:`notify` command.

All options:

.. code-block:: python

    >>> data = {
    ...    'message': 'Hi!',
    ...    'subject': 'Hello!',
    ...    'to': [
    ...        'foo@.bar.com',
    ...        'bla@boo.baz'
    ...    ],
    ...    'from': 'baz@baz.baz',
    ...    'attachments': [
    ...        '/path/to/file1', # String or pathlib.Path
    ...        Path('path/to/file2')
    ...    ],
    ...    'host': 'localhost',
    ...    'port': 25,
    ...    'username': 'foo',
    ...    'password': 'bar',
    ...    'tls': True,
    ...    'ssl': True,
    ...    'html': True
    ... }
    >>> email.notify(**data)

