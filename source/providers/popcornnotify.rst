PopcornNotify
-------------
Send `PopcornNotify <https://popcornnotify.com/>`_ notifications

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> popcornnotify = get_notifier('popcornnotify')
    >>> popcornnotify.notify(
    ...     message='Hi!',
    ...     api_key='SECRET',
    ...     recipients=[
    ...         'foo@bar.com',
    ...     ],
    ...     subject='Message subject!'
    ... )
