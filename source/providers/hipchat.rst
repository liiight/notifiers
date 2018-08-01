Hipchat
-------
Send notification to `Hipchat <https://www.hipchat.com/docs/apiv2>`_ rooms

Simple example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> hipchat = get_notifier('hipchat')
    >>> hipchat.notify(token='SECRET', group='foo', message='hi!', room=1234)

Hipchat requires using either a ``group`` or a ``team_server`` key word (for private instances

All options:

.. code-block:: python

    >>> hipchat.notify(
    ...    token='SECRET',
    ...    group='foo',
    ...    message='hi!',
    ...    card=dict(
    ...        style='image',
    ...        title='foo image'
    ...    ),
    ...    id='card ID',
    ...    icon='https://path.to/icon.png',
    ...    room=2131
    ... )

You can view the users you can send to via the ``users`` resource:

.. code-block:: python

    >>> hipchat.users(token='SECRET', group='foo')
    {'items': [{'id': 1, 'links': {'self': '...'}, 'mention_name': '...', 'name': '...', 'version': 'E4GX9340'}, ...]}

You can view the users you can send to via the ``rooms`` resource:

.. code-block:: python

    >>> hipchat.rooms(token='SECRET', group='foo')
    {'items': [{'id': 9, 'is_archived': False, ... }]
