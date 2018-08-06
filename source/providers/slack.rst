Slack (Webhooks)
----------------

Send `Slack <https://api.slack.com/>`_ webhook notifications.

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> slack = get_notifier('slack')
    >>> slack.notify(message='Hi!', webhook_url='https://url.to/webhook')

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      attachments:
        items:
          additionalProperties: false
          properties:
            author_icon:
              title: A valid URL that displays a small 16x16px image to the left of the
                author_name text. Will only work if author_name is present
              type: string
            author_link:
              title: A valid URL that will hyperlink the author_name text mentioned above.
                Will only work if author_name is present
              type: string
            author_name:
              title: Small text used to display the author's name
              type: string
            color:
              title: Can either be one of 'good', 'warning', 'danger', or any hex color
                code
              type: string
            fallback:
              title: A plain-text summary of the attachment. This text will be used in
                clients that don't show formatted text (eg. IRC, mobile notifications)
                and should not contain any markup.
              type: string
            fields:
              items:
                additionalProperties: false
                properties:
                  short:
                    title: Optional flag indicating whether the `value` is short enough
                      to be displayed side-by-side with other values
                    type: boolean
                  title:
                    title: Required Field Title
                    type: string
                  value:
                    title: Text value of the field. May contain standard message markup
                      and must be escaped as normal. May be multi-line
                    type: string
                required:
                - title
                type: object
              minItems: 1
              title: Fields are displayed in a table on the message
              type: array
            footer:
              title: Footer text
              type: string
            footer_icon:
              format: uri
              title: Footer icon URL
              type: string
            image_url:
              format: uri
              title: Image URL
              type: string
            pretext:
              title: Optional text that should appear above the formatted data
              type: string
            text:
              title: Optional text that should appear within the attachment
              type: string
            thumb_url:
              format: uri
              title: Thumbnail URL
              type: string
            title:
              title: Attachment title
              type: string
            title_link:
              title: Attachment title URL
              type: string
            ts:
              format: timestamp
              title: Provided timestamp (epoch)
              type:
              - integer
              - string
          required:
          - fallback
          type: object
        type: array
      channel:
        title: override default channel or private message
        type: string
      icon_emoji:
        title: override bot icon with emoji name.
        type: string
      icon_url:
        format: uri
        title: override bot icon with image URL
        type: string
      message:
        title: This is the text that will be posted to the channel
        type: string
      unfurl_links:
        title: avoid automatic attachment creation from URLs
        type: boolean
      username:
        title: override the displayed bot name
        type: string
      webhook_url:
        format: uri
        title: the webhook URL to use. Register one at https://my.slack.com/services/new/incoming-webhook/
        type: string
    required:
    - webhook_url
    - message
    type: object

