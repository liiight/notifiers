Telegram
--------
Send `Telegram <https://telegram.org/>`_ notifications.

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> telegram = get_notifier('telegram')
    >>> telegram.notify(message='Hi!', token='TOKEN', chat_id=1234)
    
See `here <https://stackoverflow.com/a/32572159/10251805>` for an example how to retrieve the ``chat_id`` for your bot.

You can view the available updates you can access via the ``updates`` resource

.. code-block:: python

    >>> telegram.updates(token="SECRET_TOKEN")
    {'id': '...', 'name': 'Foo/bar', ... }

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      chat_id:
        oneOf:
        - type: string
        - type: integer
        title: Unique identifier for the target chat or username of the target channel
          (in the format @channelusername)
      disable_notification:
        title: Sends the message silently. Users will receive a notification with no sound.
        type: boolean
      disable_web_page_preview:
        title: Disables link previews for links in this message
        type: boolean
      message:
        title: Text of the message to be sent
        type: string
      parse_mode:
        enum:
        - markdown
        - html
        title: Send Markdown or HTML, if you want Telegram apps to show bold, italic,
          fixed-width text or inline URLs in your bot's message.
        type: string
      reply_to_message_id:
        title: If the message is a reply, ID of the original message
        type: integer
      token:
        title: Bot token
        type: string
    required:
    - message
    - chat_id
    - token
    type: object

