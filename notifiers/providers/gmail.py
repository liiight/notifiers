"""
Send emails via `Gmail <https://www.google.com/gmail/about/>`_

This is a private use case of the :class:`~notifiers.providers.email.SMTP` provider

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> gmail = get_notifier('gmail')
    >>> gmail.defaults
    {'subject': "New email from 'notifiers'!", 'from': <USERNAME@HOST>', 'host': 'smtp.gmail.com', 'port': 587, 'tls': True, 'ssl': False, 'html': False}

    >>> gmail.notify(to='email@addrees.foo', message='hi!')
"""
from . import email


class Gmail(email.SMTP):
    """Send email via Gmail"""
    site_url = 'https://www.google.com/gmail/about/'
    base_url = 'smtp.gmail.com'
    name = 'gmail'

    @property
    def defaults(self) -> dict:
        data = super().defaults
        data['host'] = self.base_url
        data['port'] = 587
        data['tls'] = True
        return data
