Hipchat
-------
Send notification to `Hipchat <https://www.hipchat.com/docs/apiv2>`_ rooms

Simple example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> hipchat = get_notifier('hipchat')
    >>> hipchat.notify(token='SECRET', group='foo', message='hi!', room=1234)

Hipchat requires using either a ``group`` or a ``team_server`` key word (for private instances)

You can view the users you can send to via the ``users`` resource:

.. code-block:: python

    >>> hipchat.users(token='SECRET', group='foo')
    {'items': [{'id': 1, 'links': {'self': '...'}, 'mention_name': '...', 'name': '...', 'version': 'E4GX9340'}, ...]}

You can view the rooms you can send to via the ``rooms`` resource:

.. code-block:: python

    >>> hipchat.rooms(token='SECRET', group='foo')
    {'items': [{'id': 9, 'is_archived': False, ... }]


Full schema:

.. code-block:: yaml

    additionalProperties: false
    allOf:
    - required:
      - message
      - id
      - token
    - error_oneOf: Only one of 'room' or 'user' is allowed
      oneOf:
      - required:
        - room
      - required:
        - user
    - error_oneOf: Only one 'group' or 'team_server' is allowed
      oneOf:
      - required:
        - group
      - required:
        - team_server
    properties:
      attach_to:
        title: The message id to to attach this notification to
        type: string
      card:
        additionalProperties: false
        properties:
          activity:
            additionalProperties: false
            properties:
              html:
                title: Html for the activity to show in one line a summary of the action
                  that happened
                type: string
              icon:
                oneOf:
                - title: The url where the icon is
                  type: string
                - additionalProperties: false
                  properties:
                    url:
                      title: The url where the icon is
                      type: string
                    url@2x:
                      title: The url for the icon in retina
                      type: string
                  required:
                  - url
                  type: object
            required:
            - html
            type: object
          attributes:
            items:
              additionalProperties: false
              properties:
                label:
                  maxLength: 50
                  minLength: 1
                  title: Attribute label
                  type: string
                value:
                  properties:
                    icon:
                      oneOf:
                      - title: The url where the icon is
                        type: string
                      - additionalProperties: false
                        properties:
                          url:
                            title: The url where the icon is
                            type: string
                          url@2x:
                            title: The url for the icon in retina
                            type: string
                        required:
                        - url
                        type: object
                    label:
                      title: The text representation of the value
                      type: string
                    style:
                      enum:
                      - lozenge-success
                      - lozenge-error
                      - lozenge-current
                      - lozenge-complete
                      - lozenge-moved
                      - lozenge
                      title: AUI Integrations for now supporting only lozenges
                      type: string
                    url:
                      title: Url to be opened when a user clicks on the label
                      type: string
                  type: object
              required:
              - label
              - value
              type: object
            title: List of attributes to show below the card
            type: array
          description:
            oneOf:
            - type: string
            - additionalProperties: false
              properties:
                format:
                  enum:
                  - text
                  - html
                  title: Determines how the message is treated by our server and rendered
                    inside HipChat applications
                  type: string
                value:
                  maxLength: 1000
                  minLength: 1
                  type: string
              required:
              - value
              - format
              type: object
          format:
            enum:
            - compact
            - medium
            title: Application cards can be compact (1 to 2 lines) or medium (1 to 5 lines)
            type: string
          style:
            enum:
            - file
            - image
            - application
            - link
            - media
            title: Type of the card
            type: string
          thumbnail:
            additionalProperties: false
            properties:
              height:
                title: The original height of the image
                type: integer
              url:
                maxLength: 250
                minLength: 1
                title: The thumbnail url
                type: string
              url@2x:
                maxLength: 250
                minLength: 1
                title: The thumbnail url in retina
                type: string
              width:
                title: The original width of the image
                type: integer
            required:
            - url
            type: object
          title:
            maxLength: 500
            minLength: 1
            title: The title of the card
            type: string
          url:
            title: The url where the card will open
            type: string
        required:
        - style
        - title
        type: object
      color:
        enum:
        - yellow
        - green
        - red
        - purple
        - gray
        - random
        title: Background color for message
        type: string
      from:
        title: A label to be shown in addition to the sender's name
        type: string
      group:
        title: HipChat group name
        type: string
      icon:
        oneOf:
        - title: The url where the icon is
          type: string
        - additionalProperties: false
          properties:
            url:
              title: The url where the icon is
              type: string
            url@2x:
              title: The url for the icon in retina
              type: string
          required:
          - url
          type: object
      id:
        title: An id that will help HipChat recognise the same card when it is sent multiple
          times
        type: string
      message:
        maxLength: 10000
        minLength: 1
        title: The message body
        type: string
      message_format:
        enum:
        - text
        - html
        title: Determines how the message is treated by our server and rendered inside
          HipChat applications
        type: string
      notify:
        title: Whether this message should trigger a user notification (change the tab
          color, play a sound, notify mobile phones, etc). Each recipient's notification
          preferences are taken into account.
        type: boolean
      room:
        maxLength: 100
        minLength: 1
        title: The id or url encoded name of the room
        type: string
      team_server:
        title: 'An alternate team server. Example: ''https://hipchat.corp-domain.com'''
        type: string
      token:
        title: User token
        type: string
      user:
        title: The id, email address, or mention name (beginning with an '@') of the user
          to send a message to.
        type: string
    type: object