Pagerduty
---------

Open `Pagerduty <https://www.pagerduty.com>`_ incidents

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pagerduty = get_notifier('pagerduty')
    >>> images = [
    ...     {
    ...         'src': 'https://software.opensuse.org/package/thumbnail/python-Pillow.png',
    ...         'href': 'https://github.com/liiight/notifiers',
    ...         'alt': 'Notifiers'
    ...     }
    ... ]
    >>> links = [
    ...     {
    ...         'href': 'https://github.com/notifiers/notifiers',
    ...         'text': 'Python Notifiers'
    ...     }
    ... ]
    ... data = {
    ...     'message': 'foo',
    ...     'event_action': 'trigger',
    ...     'source': 'bar',
    ...     'severity': 'info',
    ...     'timestamp': datetime.datetime.now().isoformat(),
    ...     'component': 'baz',
    ...     'group': 'bla',
    ...     'class': 'buzu',
    ...     'custom_details': {
    ...         'foo': 'bar',
    ...         'boo': 'yikes'
    ...     },
    ...     'images': images,
    ...     'links': links
    ... }
    >>> pagerduty.notify(**data)
