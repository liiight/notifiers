StatusPage
----------
Send `StatusPage.io <https://statuspage.io>`_ notifications

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> statuspage = get_notifier('statuspage')
    >>> statuspage.notify(message='Hi!', api_key='KEY', page_id='123ABC')

Full schema:

.. code-block:: yaml

    additionalProperties: false
    dependencies:
      backfill_date:
      - backfilled
      backfilled:
      - backfill_date
      scheduled_auto_completed:
      - scheduled_for
      scheduled_auto_in_progress:
      - scheduled_for
      scheduled_for:
      - scheduled_until
      scheduled_remind_prior:
      - scheduled_for
      scheduled_until:
      - scheduled_for
    properties:
      api_key:
        title: OAuth2 token
        type: string
      backfill_date:
        format: date
        title: Date of incident in YYYY-MM-DD format
        type: string
      backfilled:
        title: Create an historical incident
        type: boolean
      body:
        title: The initial message, created as the first incident update
        type: string
      component_ids:
        items:
          type: string
        title: List of components whose subscribers should be notified (only applicable
          for pages with component subscriptions enabled)
        type: array
      deliver_notifications:
        title: Control whether notifications should be delivered for the initial incident
          update
        type: boolean
      impact_override:
        enum:
        - none
        - minor
        - major
        - critical
        title: Override calculated impact value
        type: string
      message:
        title: The name of the incident
        type: string
      page_id:
        title: Page ID
        type: string
      scheduled_auto_completed:
        title: Automatically transition incident to 'Completed' at end
        type: boolean
      scheduled_auto_in_progress:
        title: Automatically transition incident to 'In Progress' at start
        type: boolean
      scheduled_for:
        format: iso8601
        title: Time the scheduled maintenance should begin
        type: string
      scheduled_remind_prior:
        title: Remind subscribers 60 minutes before scheduled start
        type: boolean
      scheduled_until:
        format: iso8601
        title: Time the scheduled maintenance should end
        type: string
      status:
        enum:
        - investigating
        - identified
        - monitoring
        - resolved
        - scheduled
        - in_progress
        - verifying
        - completed
        title: Status of the incident
        type: string
      wants_twitter_update:
        title: Post the new incident to twitter
        type: boolean
    required:
    - message
    - api_key
    - page_id
    type: object

