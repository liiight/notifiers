Join
----
Send notification via `Join <https://joaoapps.com/join/>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> join = get_notifier('join')
    >>> join.notify(apikey='SECRET', message='Hi!')

You can view the devices you can send to via the ``devices`` resource:

.. code-block:: python

    >>> join.devices(apikey='SECRET')
    {'items': [{'id': 9, 'is_archived': False, ... }]

Full schema:

.. code-block:: yaml

    additionalProperties: false
    anyOf:
    - dependencies:
        smsnumber:
        - smstext
    - dependencies:
        smsnumber:
        - mmsfile
    dependencies:
      callnumber:
      - smsnumber
      smstext:
      - smsnumber
    error_anyOf: Must use either 'smstext' or 'mmsfile' with 'smsnumber'
    properties:
      alarmVolume:
        title: set device alarm volume
        type: string
      apikey:
        title: user API key
        type: string
      callnumber:
        title: number to call to
        type: string
      clipboard:
        title: "some text you want to set on the receiving device\u2019s clipboard"
        type: string
      deviceId:
        title: The device ID or group ID of the device you want to send the message to
        type: string
      deviceIds:
        oneOf:
        - items:
            title: A comma separated list of device IDs you want to send the push to
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: A comma separated list of device IDs you want to send the push to
          type: string
      deviceNames:
        oneOf:
        - items:
            title: A comma separated list of device names you want to send the push to
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: A comma separated list of device names you want to send the push to
          type: string
      file:
        format: uri
        title: a publicly accessible URL of a file
        type: string
      find:
        title: set to true to make your device ring loudly
        type: boolean
      group:
        title: allows you to join notifications in different groups
        type: string
      icon:
        format: uri
        title: notification's icon URL
        type: string
      image:
        format: uri
        title: Notification image URL
        type: string
      interruptionFilter:
        maximum: 4
        minimum: 1
        title: set interruption filter mode
        type: integer
      mediaVolume:
        title: set device media volume
        type: integer
      message:
        title: usually used as a Tasker or EventGhost command. Can also be used with URLs
          and Files to add a description for those elements
        type: string
      mmsfile:
        format: uri
        title: publicly accessible mms file url
        type: string
      priority:
        maximum: 2
        minimum: -2
        title: control how your notification is displayed
        type: integer
      ringVolume:
        title: set device ring volume
        type: string
      smallicon:
        format: uri
        title: Status Bar Icon URL
        type: string
      smsnumber:
        title: phone number to send an SMS to
        type: string
      smstext:
        title: some text to send in an SMS
        type: string
      title:
        title: "If used, will always create a notification on the receiving device with\
          \ this as the title and text as the notification\u2019s text"
        type: string
      url:
        format: uri
        title: ' A URL you want to open on the device. If a notification is created with
          this push, this will make clicking the notification open this URL'
        type: string
      wallpaper:
        format: uri
        title: a publicly accessible URL of an image file
        type: string
    required:
    - apikey
    - message
    type: object