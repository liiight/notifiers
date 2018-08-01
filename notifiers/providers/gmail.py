"""
Send emails via `GMail <https://www.google.com/gmail/about/>`_

.. code-block:: python

    >> from notifiers import get_notifier
    >> gmail = get_notifiers('gmail')
    >> gmail.notify(to='email@addrees.foo', message='hi!')
"""
from . import email


class Gmail(email.SMTP):
    """Send email via GMail"""
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
