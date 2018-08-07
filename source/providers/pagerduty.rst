Pagerduty
---------

Open `Pagerduty <https://www.pagerduty.com>`_ incidents

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> pagerduty = get_notifier('pagerduty')
    >>> pagerduty.notify(
    ...     message='Oh oh...',
    ...     event_action='trigger',
    ...     source='prod',
    ...     severity='info'
    ... )

Full schema:

.. code-block:: yaml

    properties:
      class:
        title: The class/type of the event
        type: string
      component:
        title: Component of the source machine that is responsible for the event
        type: string
      custom_details:
        title: Additional details about the event and affected system
        type: object
      dedup_key:
        maxLength: 255
        title: Deduplication key for correlating triggers and resolves
        type: string
      event_action:
        enum:
        - trigger
        - acknowledge
        - resolve
        title: The type of event
        type: string
      group:
        title: Logical grouping of components of a service
        type: string
      images:
        items:
          additionalProperties: false
          properties:
            alt:
              title: Optional alternative text for the image
              type: string
            href:
              title: Optional URL; makes the image a clickable link
              type: string
            src:
              title: The source of the image being attached to the incident. This image
                must be served via HTTPS.
              type: string
          required:
          - src
          type: object
        type: array
      links:
        items:
          additionalProperties: false
          properties:
            href:
              title: URL of the link to be attached
              type: string
            text:
              title: Plain text that describes the purpose of the link, and can be used
                as the link's text
              type: string
          required:
          - href
          - text
          type: object
        type: array
      message:
        title: A brief text summary of the event, used to generate the summaries/titles
          of any associated alerts
        type: string
      routing_key:
        title: The GUID of one of your Events API V2 integrations. This is the "Integration
          Key" listed on the Events API V2 integration's detail page
        type: string
      severity:
        enum:
        - critical
        - error
        - warning
        - info
        title: The perceived severity of the status the event is describing with respect
          to the affected system
        type: string
      source:
        title: The unique location of the affected system, preferably a hostname or FQDN
        type: string
      timestamp:
        format: iso8601
        title: The time at which the emitting tool detected or generated the event in
          ISO 8601
        type: string
    required:
    - routing_key
    - event_action
    - source
    - severity
    - message
    type: object
