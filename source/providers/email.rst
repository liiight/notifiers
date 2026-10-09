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
    {'subject': "New email from 'notifiers'!", 'from': 'notifiers@<hostname>', 'host': 'localhost', 'port': 25, 'tls': False, 'ssl': False, 'html': False, 'login': True}

Any of these can be overridden by sending them to the :func:`notify` command.
``from`` can also be passed as ``from_``. ``to``, ``cc``, ``bcc`` and ``attachments`` take a single value or a list.
``username`` and ``password`` must be passed together.

Logging in to a server over TLS:

.. code-block:: python

    >>> email.notify(
    ...     to=['first@foo.com', 'second@foo.com'],
    ...     message='hi!',
    ...     host='smtp.foo.com',
    ...     port=587,
    ...     tls=True,
    ...     username='me@foo.com',
    ...     password='SECRET',
    ...     attachments='/path/to/report.pdf',
    ... )

Arguments:

.. provider-arguments:: email

