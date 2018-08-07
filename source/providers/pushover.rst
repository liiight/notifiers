Pushover
--------

Send `Pushover <https://pushover.net/>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pushover = get_notifier('pushover')
    >>> pushover.notify(message='Hi!', user='USER', token='TOKEN')

You can view the sounds you can user in the notification via the ``sounds`` resource:

.. code-block:: python

    >>> pushover.sounds(token='SECRET')
    ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming', 'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb', 'persistent', 'echo', 'updown', 'none']

You can view the limits of your application token using the  ``limits`` resource:

.. code-block:: python

    >>> pushover.limits(token='SECRET')
    {'limit': 7500, 'remaining': 6841, 'reset': 1535778000, 'status': 1, 'request': 'f0cb73b1-810d-4b9a-b275-394481bceb74'}

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      attachment:
        format: valid_file
        title: an image attachment to send with the message
        type: string
      callback:
        format: uri
        title: a publicly-accessible URL that our servers will send a request to when
          the user has acknowledged your notification. priority must be set to 2
        type: string
      device:
        oneOf:
        - items:
            title: your user's device name to send the message directly to that device
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: your user's device name to send the message directly to that device
          type: string
      expire:
        maximum: 86400
        title: how many seconds your notification will continue to be retried for. priority
          must be set to 2
        type: integer
      html:
        title: enable HTML formatting
        type: boolean
      message:
        title: your message
        type: string
      priority:
        maximum: 2
        minimum: -2
        title: notification priority
        type: integer
      retry:
        minimum: 30
        title: how often (in seconds) the Pushover servers will send the same notification
          to the user. priority must be set to 2
        type: integer
      sound:
        title: the name of one of the sounds supported by device clients to override the
          user's default sound choice. See `sounds` resource
        type: string
      timestamp:
        format: timestamp
        minimum: 0
        title: a Unix timestamp of your message's date and time to display to the user,
          rather than the time your message is received by our API
        type:
        - integer
        - string
      title:
        title: your message's title, otherwise your app's name is used
        type: string
      token:
        title: your application's API token
        type: string
      url:
        format: uri
        title: a supplementary URL to show with your message
        type: string
      url_title:
        title: a title for your supplementary URL, otherwise just the URL is shown
        type: string
      user:
        oneOf:
        - items:
            title: the user/group key (not e-mail address) of your user (or you)
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: the user/group key (not e-mail address) of your user (or you)
          type: string
    required:
    - user
    - message
    - token
    type: object
