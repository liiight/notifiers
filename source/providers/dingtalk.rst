DingTalk
----------
Send `DingTalk Robot <https://dingtalk.com/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> dingtalk = get_notifier('dingtalk')
    >>> dingtalk.notify(access_token='token', message='Hi there!')

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      access_token:
        title: your access token
        type: string
      message:
        title: message content
        type: string
    required:
    - access_token
    - message
    type: object

