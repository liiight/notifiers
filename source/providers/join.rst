Join
----
Send notification via `Join <https://joaoapps.com/join/>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> join = get_notifier('join')
    >>> join.notify(apikey='SECRET', message='Hi!')

All options:

.. code-block:: python

    >>> data = {
    ...     'message': 'Hi!,
    ...     'apikey': 'SECRET',
    ...     'deviceId': '12345ABCDE',
    ...     'deviceIds': [
    ...         '12345ABCDE',
    ...         'ABCDE12345'
    ...     ],
    ...     'deviceNames': [
    ...         'foo',
    ...         'bar'
    ...     ],
    ...     'url': 'https://url.to/add',
    ...     'clipboard': 'paste this',
    ...     'file': 'https://path.to/file.txt',
    ...     'smsnumber': '+123456789',
    ...     'smstext': 'SMS text',
    ...     'callnumber': '+123456789',
    ...     'interruptionFilter': 3,
    ...     'mmsfile': 'https://path.to/file.txt',
    ...     'mediaVolume': 13,
    ...     'ringVolume': 13,
    ...     'alarmVolume': 13,
    ...     'wallpaper': 'https://path.to/img.jpg',
    ...     'find': True,
    ...     'title': 'Notification title'
    ...     'icon': 'https://path.to/img.jpg',
    ...     'smallicon': 'https://path.to/img.jpg',
    ...     'priority': 0,
    ...     'group': 'foo',
    ...     'image': 'https://path.to/img.jpg'
    ... }
    >>> join.notify(**data)

