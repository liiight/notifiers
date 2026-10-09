Slack (Webhooks)
----------------

Send `Slack <https://api.slack.com/>`_ webhook notifications.

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> slack = get_notifier('slack')
    >>> slack.notify(message='Hi!', webhook_url='https://url.to/webhook')

Arguments:

.. provider-arguments:: slack
