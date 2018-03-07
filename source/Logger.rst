.. _notification_logger:

Notification logger
-------------------

Notifiers enable you to log directly to a notifier via a stdlib logging handler, :class:`~notifiers.logging.NotificationHandler`:

.. code-block:: python

    >>> import logging
    >>> from notifiers.logging import NotificationHandler

    >>> log = logging.getLogger(__name__)
    >>> defaults = {
            'token': 'foo,
            'user': 'bar
        }

    >>> hdlr = NotificationHandler('pushover', defaults=defaults)
    >>> hdlr.setLevel(logging.ERROR)

    >>> log.addHandler(hdlr)
    >>> log.error('And just like that, you get notified about all your errors!')

By setting the handler level to the desired one, you can directly get notified about relevant event in your application, without needing to change a single line of code.

Using environs
==============

Like any other usage of notifiers, you can pass any relevant provider arguments via :ref:`environs`.

Fallback notifiers
==================

If you rely on 3rd party notifiers to send you notification about errors, you may want to have a fallback in case those notification fail for any reason. You can define a fallback notifier like so:

.. code-block:: python

    >>> fallback_defaults = {
        'host': 'http://localhost,
        'port': 80,
        'username': 'foo',
        'password': 'bar
    }

    >>> hdlr = NotificationHandler('pushover', fallback='email', fallback_defaults=fallback_defaults)

Then in case there is an error with the main notifier, ``pushover`` in this case, you'll get a notification sent via ``email``.

.. note::

   :class:`~notifiers.logging.NotificationHandler` respect the standard :mod:`logging` ``raiseExceptions`` flag to determine if fallback should be used. Also, fallback is used only when any subclass of :class:`~notifiers.exceptions.NotifierException` occurs.


