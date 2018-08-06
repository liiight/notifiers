Mailgun
-------
Send notification via `Mailgun <https://www.mailgun.com/>`_

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> mailgun = get_notifiers('mailgun')
    >>> mailgun.notify(to='foo@bar.baz', domain='mydomain', api_key='SECRET', message='Hi!')

Full schema:

.. code-block:: yaml

    additionalProperties: false
    allOf:
    - required:
      - to
      - domain
      - api_key
    - anyOf:
      - required:
        - from
      - required:
        - from_
    - anyOf:
      - required:
        - message
      - required:
        - html
      error_anyOf: Need either "message" or "html"
    properties:
      api_key:
        title: User's API key
        type: string
      attachment:
        oneOf:
        - items:
            format: valid_file
            title: File attachment
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - format: valid_file
          title: File attachment
          type: string
      bcc:
        oneOf:
        - items:
            title: 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'
          type: string
      cc:
        oneOf:
        - items:
            title: 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'
          type: string
      data:
        additionalProperties:
          type: object
        title: attach a custom JSON data to the message
        type: object
      deliverytime:
        format: rfc2822
        title: 'Desired time of delivery. Note: Messages can be scheduled for a maximum
          of 3 days in the future.'
        type: string
      dkim:
        title: Enables/disables DKIM signatures on per-message basis
        type: boolean
      domain:
        title: MailGun's domain to use
        type: string
      from:
        format: email
        title: Email address for From header
        type: string
      from_:
        duplicate: true
        format: email
        title: Email address for From header
        type: string
      headers:
        additionalProperties:
          type: string
        title: Any other header to add
        type: object
      html:
        title: Body of the message. (HTML version)
        type: string
      inline:
        oneOf:
        - items:
            format: valid_file
            title: Attachment with inline disposition. Can be used to send inline images
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - format: valid_file
          title: Attachment with inline disposition. Can be used to send inline images
          type: string
      message:
        title: Body of the message. (text version)
        type: string
      require_tls:
        title: If set to True this requires the message only be sent over a TLS connection.
          If a TLS connection can not be established, Mailgun will not deliver the message.If
          set to False, Mailgun will still try and upgrade the connection, but if Mailgun
          can not, the message will be delivered over a plaintext SMTP connection.
        type: boolean
      skip_verification:
        title: If set to True, the certificate and hostname will not be verified when
          trying to establish a TLS connection and Mailgun will accept any certificate
          during delivery. If set to False, Mailgun will verify the certificate and hostname.
          If either one can not be verified, a TLS connection will not be established.
        type: boolean
      subject:
        title: Message subject
        type: string
      tag:
        oneOf:
        - items:
            format: ascii
            maxLength: 128
            title: Tag string
            type: string
          maxItems: 3
          minItems: 1
          type: array
          uniqueItems: true
        - format: ascii
          maxLength: 128
          title: Tag string
          type: string
      testmode:
        title: Enables sending in test mode.
        type: boolean
      to:
        oneOf:
        - items:
            title: 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - title: 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'
          type: string
      tracking:
        title: Toggles tracking on a per-message basis
        type: boolean
      tracking_clicks:
        enum:
        - true
        - false
        - htmlonly
        title: Toggles clicks tracking on a per-message basis. Has higher priority than
          domain-level setting. Pass yes, no or htmlonly.
        type:
        - string
        - boolean
      tracking_opens:
        title: Toggles opens tracking on a per-message basis. Has higher priority than
          domain-level setting
        type: boolean
    type: object
