Telegram
--------
Send `Telegram <https://telegram.org/>`_ notifications.

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> telegram = get_notifier('telegram')
    >>> telegram.notify(message='Hi!', token='TOKEN', chat_id=1234)

See `here <https://stackoverflow.com/a/32572159/10251805>` for an example how to retrieve the ``chat_id`` for your bot.

You can view the available updates you can access via the ``updates`` resource

.. code-block:: python

    >>> telegram.updates(token="SECRET_TOKEN")
    {'id': '...', 'name': 'Foo/bar', ... }

Arguments:

.. provider-arguments:: telegram
