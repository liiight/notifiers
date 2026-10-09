Zulip
-----
Send `Zulip <https://zulipchat.com/>`_ notifications

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> zulip = get_notifier('zulip')
    >>> zulip.notify(message='Hi!', to='foo', email='foo@bar.com', api_key='KEY', domain='foobar')

Arguments:

.. provider-arguments:: zulip
