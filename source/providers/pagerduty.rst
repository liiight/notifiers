Pagerduty
---------

Open `Pagerduty <https://www.pagerduty.com>`_ incidents

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pagerduty = get_notifier('pagerduty')
    >>> pagerduty.notify(
    ...     message='Oh oh...',
    ...     event_action='trigger',
    ...     source='prod',
    ...     severity='info'
    ... )

Arguments:

.. provider-arguments:: pagerduty
