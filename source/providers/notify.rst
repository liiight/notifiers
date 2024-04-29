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

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      title:
        title: Title of the message
        type: string
      message:
        title: Body of the message
        type: string
      base_url:
        title: URL of the Notify instance
        type: string
        description: |
          The URL of the Notify instance. For example, if you are using the the demo instance you would use ``https://notify-demo.deno.dev``.
      tags:
        title: Tags to send the notification to
        type: array
        items:
          type: string
      token:
        title: access token
        type: string
    required:
    - title
    - message
    - base_url
    type: object
