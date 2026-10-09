StatusPage
----------
Send `StatusPage.io <https://statuspage.io>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> statuspage = get_notifier('statuspage')
    >>> statuspage.notify(message='Hi!', api_key='KEY', page_id='123ABC')

You can view the components you use in the notification via the ``components`` resource:

.. code-block:: python

    >>> statuspage.components(api_key='KEY', page_id='123ABC')
    [{'id': '...', 'page_id': '...', ...]

Arguments:

.. provider-arguments:: statuspage
