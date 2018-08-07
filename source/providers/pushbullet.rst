Pushbullet
----------
Send `Pushbullet <https://www.pushbullet.com>`_ notifications.

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pushbullet = get_notifier('pushbullet')
    >>> pushbullet.notify(
    ...     message='Hi!',
    ...     token='SECRET',
    ...     title='Message title',
    ...     type_='note',
    ...     url='https://url.in/message',
    ...     source_device_iden='FOO',
    ...     device_iden='bar',
    ...     client_iden='baz',
    ...     channel_tag='channel tag',
    ...     email='foo@bar.com',
    ...     guid='1234abcd',
    ... )

You can view the devices you can send to via the ``devices`` resource:

.. code-block:: python

    >>> pushbullet.devices(token='SECRET')
    [{'active': True, 'iden': ... }]

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      channel_tag:
        title: Channel tag of the target channel, sends a push to all people who are subscribed
          to this channel. The current user must own this channel.
        type: string
      client_iden:
        title: Client iden of the target client, sends a push to all users who have granted
          access to this client. The current user must own this client
        type: string
      device_iden:
        title: Device iden of the target device, if sending to a single device
        type: string
      email:
        format: email
        title: Email address to send the push to. If there is a pushbullet user with this
          address, they get a push, otherwise they get an email
        type: string
      guid:
        title: Unique identifier set by the client, used to identify a push in case you
          receive it from /v2/everything before the call to /v2/pushes has completed.
          This should be a unique value. Pushes with guid set are mostly idempotent, meaning
          that sending another push with the same guid is unlikely to create another push
          (it will return the previously created push).
        type: string
      message:
        title: Body of the push
        type: string
      source_device_iden:
        title: Device iden of the sending device
        type: string
      title:
        title: Title of the push
        type: string
      token:
        title: API access token
        type: string
      type:
        enum:
        - note
        - link
        title: Type of the push, one of "note" or "link"
        type: string
      type_:
        enum:
        - note
        - link
        title: Type of the push, one of "note" or "link"
        type: string
      url:
        title: URL field, used for type="link" pushes
        type: string
    required:
    - message
    - token
    type: object
