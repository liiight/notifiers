VictorOps (REST)
--------------------

Send `VictorOps <https://alert.victorops.com/integrations/generic>`_ rest integration notifications.

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> victorops = get_notifier('victorops')
    >>> victorops.notify(rest_url='https://alert.victorops.com/integrations/generic/20131114/alert/f7dc2eeb-26dd-43b8-9ed2-0f08879f4ec2/cost_alerts',
                         message_type='CRITICAL',
                         entity_id='foo testing',
                         entity_display_name="bla test title text",
                         state_message="bla message description")

Full schema:

.. code-block:: yaml

    additionalProperties: false
    properties:
      rest_url:
          type: string
          format: uri
          title: the REST URL to use with routing_key, create one in victorops integrations tab.

      message_type:
          type: string
          title: severity level can be:
                   - CRITICAL or WARNING: Triggers an incident
                   - ACKNOWLEDGEMENT: Acks an incident
                   - INFO: Creates a timeline event but doesn't trigger an incident
                   - RECOVERY: Resolves an incident

      entity_id:
          type: string
          title: Unique id for the incident for aggregation acking or resolving.

      entity_display_name:
          type: string
          title: Display Name in the UI and Notifications.

      state_message:
          type: string
          title: This is the description that will be posted in the incident.

      annotations:
          type: object
          format:
              vo_annotate.s.Note: annotation
              vo_annotate.u.Runbook: annotation
              vo_annotate.i.Graph: annotation
          title: annotations can be of three types vo_annotate.u.Runbook vo_annotate.s.Note vo_annotate.i.image.

      additional_keys:
          type: object
          title: any additional keys that ca be passed in the body

    required:
      - rest_url
      - message_type
      - entity_id
      - entity_display_name
      - state_message
    type: object

