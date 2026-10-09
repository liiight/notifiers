Twilio
------
Send `Twilio <https://www.twilio.com/>`_ SMS

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> twilio = get_notifier('twilio')
    >>> twilio.notify(message='Hi!', to='+12345678', account_sid=1234, auth_token='TOKEN')


Arguments:

.. provider-arguments:: twilio
