iCloud
------
Send emails via `iCloud <https://www.icloud.com/mail>`_

This is a private use case of the :class:`~notifiers.providers.email.SMTP` provider, with iCloud's server as default:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> icloud = get_notifier('icloud')
    >>> icloud.defaults
    {'subject': "New email from 'notifiers'!", 'from': 'notifiers@<hostname>', 'host': 'smtp.mail.me.com', 'port': 587, 'tls': True, 'ssl': False, 'html': False, 'login': True}

    >>> icloud.notify(to='email@addrees.foo', message='hi!', username='username@icloud.com', password='my-icloud-app-password', from_='username@icloud.com')

``username`` and ``password`` are required. ``username`` must be your primary iCloud username, ``from`` (or ``from_``)
can be an iCloud alias.

Arguments:

.. provider-arguments:: icloud
