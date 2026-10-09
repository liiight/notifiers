Mailgun
-------
Send notification via `Mailgun <https://www.mailgun.com/>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> mailgun = get_notifiers('mailgun')
    >>> mailgun.notify(to='foo@bar.baz', domain='mydomain', api_key='SECRET', message='Hi!')

Arguments:

.. provider-arguments:: mailgun
