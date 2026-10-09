Pushover
--------

Send `Pushover <https://pushover.net/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pushover = get_notifier('pushover')
    >>> pushover.notify(message='Hi!', user='USER', token='TOKEN')

You can view the sounds you can user in the notification via the ``sounds`` resource:

.. code-block:: python

    >>> pushover.sounds(token='SECRET')
    ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']

You can view the limits of your application token using the  ``limits`` resource:

.. code-block:: python

    >>> pushover.limits(token='SECRET')
    {'limit': 7500, 'remaining': 6841, 'reset': 1535778000, 'status': 1, 'request': 'f0cb73b1-810d-4b9a-b275-394481bceb74'}

Arguments:

.. provider-arguments:: pushover
