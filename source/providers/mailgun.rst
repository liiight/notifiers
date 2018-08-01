Mailgun
-------
Send notification via `Mailgun <https://www.mailgun.com/>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> mailgun = get_notifiers('mailgun')
    >>> mailgun.notify(to='foo@bar.baz', domain='mydomain', api_key='SECRET', message='Hi!')


All options:

.. code-block:: python

    >>> data = {
    ...    'message': 'foo',
    ...    'html': '<b>foo</b>',
    ...    'subject': 'foo',
    ...    'attachment': [
    ...        '/path/to/file1'
    ...    ],
    ...    'inline': [
    ...        '/path/to/file2'
    ...    ],
    ...    'tag': [
    ...        'foo',
    ...        'bar'
    ...    ],
    ...    'dkim': True,
    ...    'deliverytime': 'Thu, 25 Dec 1975 14:15:16 -0500',
    ...    'testmode': False,
    ...    'tracking': True,
    ...    'tracking_clicks': 'htmlonly',
    ...    'tracking_opens': True,
    ...    'require_tls': False,
    ...    'skip_verification': True,
    ...    'headers': {
    ...        'foo': 'bar'
    ...    },
    ...    'data': {
    ...        'foo': {
    ...            'bar': 'bla'
    ...        }
    ...     }
    ... }
    >>> mailgun.notify(**data)