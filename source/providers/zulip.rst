Zulip
-----
Send `Zulip <https://zulipchat.com/>`_ notifications

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> zulip = get_notifier('zulip')
    >>> zulip.notify(message='Hi!', to='foo', email='foo@bar.com', api_key='KEY', domain='foobar')

Full schema:

.. code-block:: yaml

    additionalProperties: false
    allOf:
    - required:
      - message
      - email
      - api_key
      - to
    - error_oneOf: Only one of 'domain' or 'server' is allowed
      oneOf:
      - required:
        - domain
      - required:
        - server
    properties:
      api_key:
        title: User API Key
        type: string
      domain:
        minLength: 1
        title: Zulip cloud domain
        type: string
      email:
        format: email
        title: User email
        type: string
      message:
        title: Message content
        type: string
      server:
        format: uri
        title: 'Zulip server URL. Example: https://myzulip.server.com'
        type: string
      subject:
        title: Title of the stream message. Required when using stream.
        type: string
      to:
        title: Target of the message
        type: string
      type:
        enum:
        - stream
        - private
        title: Type of message to send
        type: string
      type_:
        enum:
        - stream
        - private
        title: Type of message to send
        type: string
    type: object

