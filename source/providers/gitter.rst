Gitter
------
Send notifications via `Gitter <https://gitter.im>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> gitter = get_notifier('gitter')
    >>> gitter.required
    {'required': ['message', 'token', 'room_id']}

    >>> gitter.notify(message='Hi!', token='SECRET_TOKEN', room_id=1234)

You can view the available rooms you can access via the ``rooms`` resource

.. code-block:: python

    >>> gitter.rooms(token="SECRET_TOKEN")
    {'id': '...', 'name': 'Foo/bar', ... }


