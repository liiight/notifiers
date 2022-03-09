DingTalk
----------
Send `DingTalk Robot <https://dingtalk.com/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> dingtalk = get_notifier('dingtalk')
    >>> dingtalk.notify(access_token='token', msg_data={'msgtype': 'text', 'text':{'content': 'Hi there!'}})

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      access_token:
        title: your access token
        type: string
      msg_data:
        title: your message definition
        type: object
    required:
    - access_token
    - msg_data
    type: object

