iCloud
-----
Send emails via `iCLoud <https://www.icloud.com/mail>`_

This is a private use case of the :class:`~notifiers.providers.email.SMTP` provider

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> icloud = get_notifier('icloud')
    >>> icloud.defaults
    {'subject': "New email from 'notifiers'!", 'from': '<USERNAME@HOST>', 'host': 'smtp.mail.me.com', 'port': 587, 'tls': True, 'ssl': False, 'html': True}

    >>> icloud.notify(to='email@addrees.foo', message='hi!', username = 'username@icloud.com', password = 'my-icloud-app-password', from_ = 'username@icloud.com')


.. code-block:: yaml
    required:
    - username
    - password
    - from_
    - to
    type: object

from_ can be an iCloud alias
username must be your primary iCloud username