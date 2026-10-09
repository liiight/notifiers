Utils
=====

Assorted helper utils

.. autofunction:: notifiers.utils.helpers.text_to_bool
.. autofunction:: notifiers.utils.helpers.merge_dicts
.. autofunction:: notifiers.utils.helpers.dict_from_environs
.. autofunction:: notifiers.utils.helpers.list_to_commas
.. autofunction:: notifiers.utils.helpers.snake_to_camel_case
.. autofunction:: notifiers.utils.helpers.valid_file

.. autoclass:: notifiers.utils.requests.RequestsHelper
   :members:

Schema models
-------------

Base model and helpers used to declare provider schemas, see :ref:`custom_providers`.

.. autoclass:: notifiers.models.SchemaModel
   :members: is_set, require_dependencies

.. autofunction:: notifiers.models.one_or_more

.. autoclass:: notifiers.models.OneOrMore

.. autofunction:: notifiers.models.required_fields

.. autofunction:: notifiers.models.model_defaults

Schema types
------------

Reusable annotated types for schema fields. They replace the custom JSON schema ``format`` checkers used before 2.0.

.. autodata:: notifiers.models.types.Email
.. autodata:: notifiers.models.types.Url
.. autodata:: notifiers.models.types.Hostname
.. autodata:: notifiers.models.types.Port
.. autodata:: notifiers.models.types.Timestamp
.. autodata:: notifiers.models.types.ISO8601Datetime
.. autodata:: notifiers.models.types.RFC2822Datetime
.. autodata:: notifiers.models.types.DateString
.. autodata:: notifiers.models.types.AsciiStr
.. autodata:: notifiers.models.types.FilePath
.. autodata:: notifiers.models.types.E164
