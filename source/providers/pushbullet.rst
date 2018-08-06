Pushbullet
----------
Send `Pushbullet <https://www.pushbullet.com>`_ notifications.

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pushbullet = get_notifier('pushbullet')
    >>> pushbullet.notify(
    ...     message='Hi!',
    ...     token='SECRET',
    ...     title='Message title',
    ...     type_='note',
    ...     url='https://url.in/message',
    ...     source_device_iden='FOO',
    ...     device_iden='bar',
    ...     client_iden='baz',
    ...     channel_tag='channel tag',
    ...     email='foo@bar.com',
    ...     guid='1234abcd',
    ... )