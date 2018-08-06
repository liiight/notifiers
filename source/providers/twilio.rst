Twilio
------
Send `Twilio <https://www.twilio.com/>`_ SMS

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> twilio = get_notifier('twilio')
    >>> twilio.notify(message='Hi!', to='+12345678', account_sid=1234, auth_token='TOKEN')


Full schema:

.. code-block:: yaml

    allOf:
    - anyOf:
      - anyOf:
        - required:
          - from
        - required:
          - from_
      - required:
        - messaging_service_id
      error_anyOf: Either 'from' or 'messaging_service_id' are required
    - anyOf:
      - required:
        - message
      - required:
        - media_url
      error_anyOf: Either 'message' or 'media_url' are required
    - required:
      - to
      - account_sid
      - auth_token
    properties:
      account_sid:
        title: The unique id of the Account that sent this message.
        type: string
      application_sid:
        title: Twilio will POST MessageSid as well as MessageStatus=sent or MessageStatus=failed
          to the URL in the MessageStatusCallback property of this Application
        type: string
      auth_token:
        title: The user's auth token
        type: string
      from:
        title: Twilio phone number or the alphanumeric sender ID used
        type: string
      from_:
        duplicate: true
        title: Twilio phone number or the alphanumeric sender ID used
        type: string
      max_price:
        title: The total maximum price up to the fourth decimal (0.0001) in US dollars
          acceptable for the message to be delivered
        type: number
      media_url:
        format: uri
        title: The URL of the media you wish to send out with the message
        type: string
      message:
        maxLength: 1600
        title: The text body of the message. Up to 1,600 characters long.
        type: string
      messaging_service_id:
        title: The unique id of the Messaging Service used with the message
        type: string
      provide_feedback:
        title: Set this value to true if you are sending messages that have a trackable
          user action and you intend to confirm delivery of the message using the Message
          Feedback API
        type: boolean
      status_callback:
        format: uri
        title: A URL where Twilio will POST each time your message status changes
        type: string
      to:
        title: The recipient of the message, in E.164 format
        format: e164
        type: string
      validity_period:
        maximum: 14400
        minimum: 1
        title: The number of seconds that the message can remain in a Twilio queue
        type: integer
    type: object
