Email (SMTP)
------------

Enables sending email messages to SMTP servers.

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> email = get_notifier('email')
    >>> email.required
    {'required': ['message', 'to']}

    >>> email.notify(to='email@addrees.foo', message='hi!')


It uses several defaults:

.. code-block:: python

    >>> email.defaults
    {'subject': "New email from 'notifiers'!", 'from': '[USER@HOSTNAME]', 'host': 'localhost', 'port': 25, 'tls': False, 'ssl': False, 'html': False}

Any of these can be overridden by sending them to the :func:`notify` command.

Full schema:

.. code-block:: yaml

    additionalProperties: false
    dependencies:
      password:
      - username
      ssl:
      - tls
      username:
      - password
    properties:
      attachments:
        oneOf:
        - items:
            format: valid_file
            title: one or more attachments to use in the email
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - format: valid_file
          title: one or more attachments to use in the email
          type: string
      from:
        format: email
        title: the FROM address to use in the email
        type: string
      from_:
        duplicate: true
        format: email
        title: the FROM address to use in the email
        type: string
      host:
        format: hostname
        title: the host of the SMTP server
        type: string
      html:
        title: should the email be parse as an HTML file
        type: boolean
      message:
        title: the content of the email message
        type: string
      password:
        title: password if relevant
        type: string
      port:
        format: port
        title: the port number to use
        type: integer
      ssl:
        title: should SSL be used
        type: boolean
      subject:
        title: the subject of the email message
        type: string
      tls:
        title: should TLS be used
        type: boolean
      to:
        oneOf:
        - items:
            format: email
            title: one or more email addresses to use
            type: string
          minItems: 1
          type: array
          uniqueItems: true
        - format: email
          title: one or more email addresses to use
          type: string
      username:
        title: username if relevant
        type: string
      login:
        title: Trigger login to server
        type: boolean
    required:
    - message
    - to
type: object
