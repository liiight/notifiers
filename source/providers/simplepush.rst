SimplePush
----------
Send `SimplePush <https://simplepush.io/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> simplepush = get_notifier('simplepush')
    >>> simplepush.notify(message='Hi!', key='KEY')

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      event:
        title: Event ID
        type: string
      key:
        title: your user key
        type: string
      message:
        title: your message
        type: string
      title:
        title: message title
        type: string
    required:
    - key
    - message
    type: object

