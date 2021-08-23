VictorOps (REST)
--------------------

Send `VictorOps <https://alert.victorops.com/integrations/generic>`_ rest integration notifications.

Minimal example:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> victorops = get_notifier('victorops')
    >>> victorops.notify(rest_url='https://alert.victorops.com/integrations/generic/20104876/alert/f7dc2eeb-ms9k-43b8-kd89-0f00000f4ec2/$routing_key',
                         message_type='CRITICAL',
                         entity_id='foo testing',
                         entity_display_name="bla test title text",
                         message="bla message description")

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
                   - critical or warning: Triggers an incident
                   - acknowledgement: Acks an incident
                   - info: Creates a timeline event but doesn't trigger an incident
                   - recovery or ok: Resolves an incident

      entity_id:
          type: string
          title: Unique id for the incident for aggregation acking or resolving.

      entity_display_name:
          type: string
          title: Display Name in the UI and Notifications.

      message:
          type: string
          title: This is the description that will be posted in the incident.

      annotations:
          type: object
          format:
              vo_annotate.s.{custom_name}: annotation
              vo_annotate.u.{custom_name}: annotation
              vo_annotate.i.{custom_name}: annotation
          title: annotations can be of three types vo_annotate.u.{custom_name} vo_annotate.s.{custom_name} vo_annotate.i.{custom_name}.

      additional_keys:
          type: object
          format:
              key: value
              key: value
              key: value
          title: any additional keys that ca be passed in the body

    required:
      - rest_url
      - message_type
      - entity_id
      - entity_display_name
      - message
    type: object

