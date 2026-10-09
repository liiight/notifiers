Join
----
Send notification via `Join <https://joaoapps.com/join/>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> join = get_notifier('join')
    >>> join.notify(apikey='SECRET', message='Hi!')

You can view the devices you can send to via the ``devices`` resource:

.. code-block:: python

    >>> join.devices(apikey='SECRET')
    {'items': [{'id': 9, 'is_archived': False, ... }]

Arguments:

.. provider-arguments:: join
