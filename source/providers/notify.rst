Notify
------

Send notifications via `Notify <https://github.com/K0IN/Notify>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> notify = get_notifier('notify')
    >>> notify.required
    {'required': ['title', 'message', 'base_url']}

    >>> notify.notify(title='Hi!', message='my message', base_url='http://localhost:8787')
    # some instances may need a token
    >>> notify.notify(title='Hi!', message='my message', base_url='http://localhost:8787', token="send_key")

Arguments:

.. provider-arguments:: notify
