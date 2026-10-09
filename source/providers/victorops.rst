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

Arguments:

.. provider-arguments:: victorops
