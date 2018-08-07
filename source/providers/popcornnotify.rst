PopcornNotify
-------------
Send `PopcornNotify <https://popcornnotify.com/>`_ notifications

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> popcornnotify = get_notifier('popcornnotify')
    >>> popcornnotify.notify(
    ...     message='Hi!',
    ...     api_key='SECRET',
    ...     recipients=[
    ...         'foo@bar.com',
    ...     ],
    ...     subject='Message subject!'
    ... )

Full schema:

.. code-block:: yaml

    properties:
      api_key:
        title: The API key
        type: string
      message:
        title: The message to send
        type: string
      recipients:
        oneOf:
        - items:
            format: email
            title: The recipient email address or phone number. Or an array of email addresses
              and phone numbers
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - format: email
          title: The recipient email address or phone number. Or an array of email addresses
            and phone numbers
          type: string
      subject:
        title: The subject of the email. It will not be included in text messages.
        type: string
    required:
    - message
    - api_key
    - recipients
    type: object

