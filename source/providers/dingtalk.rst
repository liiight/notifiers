DingTalk
--------
Send `DingTalk Robot <https://dingtalk.com/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> dingtalk = get_notifier('dingtalk')
    >>> dingtalk.notify(access_token='token', message='Hi there!')

Any message type can be sent with ``msg_data``:

.. code-block:: python

    >>> dingtalk.notify(
    ...     access_token='token',
    ...     msg_data={'msgtype': 'markdown', 'markdown': {'title': 'Report', 'text': '# All good'}},
    ...     at={'isAtAll': True},
    ... )

Arguments:

.. provider-arguments:: dingtalk
