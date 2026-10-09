SimplePush
----------
Send `SimplePush <https://simplepush.io/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> simplepush = get_notifier('simplepush')
    >>> simplepush.notify(message='Hi!', key='KEY')

Arguments:

.. provider-arguments:: simplepush
