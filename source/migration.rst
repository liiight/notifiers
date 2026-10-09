.. _migration_2_0:

Migrating to 2.0
================

In 2.0, provider schemas are `pydantic <https://docs.pydantic.dev/>`_ (v2) models instead of JSON Schema dicts
validated with ``jsonschema``.

If you only **use** notifiers, via ``notify()``, ``get_notifier()``, the CLI or the logging handler, most code keeps
working unchanged. Read :ref:`migration_users` for the behaviour changes.

If you **wrote a custom provider** (for example a plugin registered via the ``notifiers`` entry point), you need to port
its schema. See :ref:`migration_providers`.

Requirements
------------

- Python 3.10 or newer.
- ``pydantic>=2.7,<3`` replaces ``jsonschema``.

.. _migration_users:

For library users
-----------------

Unchanged
~~~~~~~~~

- ``notifiers.notify()``, ``notifiers.get_notifier()``, ``notifiers.all_providers()``
- ``Provider.notify(raise_on_errors=False, **kwargs)`` and provider resources, e.g. ``telegram.updates(token=...)``
- :class:`~notifiers.core.Response`, including ``status`` values ``"Success"`` / ``"Failure"``
- All exceptions. Invalid arguments still raise :class:`~notifiers.exceptions.BadArguments`
- Argument names of every provider, including the ``from_`` / ``type_`` spellings of the reserved words ``from`` / ``type``
- Environment variables (``NOTIFIERS_<PROVIDER>_<ARGUMENT>``) and the ``env_prefix`` argument
- :class:`~notifiers.logging.NotificationHandler`
- ``provider.schema``, ``provider.arguments``, ``provider.required`` and ``provider.defaults`` are still properties returning
  dicts

Changed
~~~~~~~

**Values are converted to their declared type.** Strings such as ``"587"`` or ``"true"`` are accepted for integer and
boolean arguments and converted. This makes environment variables usable for non string arguments, e.g.
``NOTIFIERS_EMAIL_PORT=587``. Values that can't be converted are still rejected.

**Error messages.** Missing arguments, unknown arguments and the provider specific rules keep the same wording, e.g.
``Error with sent data: 'user' is a required property``. Other errors use pydantic's wording, prefixed with the argument
name, e.g. ``Error with sent data: 'priority': Input should be less than or equal to 2``.

:class:`~notifiers.exceptions.BadArguments` has a new ``errors`` attribute holding **all** validation errors, each a dict
with ``loc``, ``msg`` and ``type`` keys.

**Schema layout.** The pydantic model is available as ``provider.schema_model``. ``provider.schema`` returns its JSON
schema exactly as pydantic generates it (``provider.schema_model.model_json_schema(by_alias=True)``), and
``provider.arguments`` returns that schema's ``properties``. The layout therefore follows pydantic, for example:

- Argument descriptions are under ``description``, and pydantic adds a ``title`` to every argument.
- Optional arguments are rendered as ``anyOf: [<type>, {type: null}]`` with ``default: null``.
- Nested models (e.g. Slack ``attachments``) are referenced via ``$defs``.
- ``from_`` is listed once, as ``from``. ``from_=`` is still accepted when sending.

``provider.required`` still returns ``{"required": [...]}``. It lists the required arguments only, conditional
requirements (e.g. "``message`` or ``html``") are enforced on validation and described in each provider's docs.

**Argument names.** Every argument keeps the name it had before 2.0. Arguments that aren't snake_case in the remote API
(e.g. Join's ``deviceId``, ``smsnumber``) can now also be passed in snake_case (``device_id``, ``sms_number``). The data
sent to the API is unchanged.

**SchemaError** is no longer raised. It can still be imported, so ``except SchemaError`` keeps working.

Provider fixes
~~~~~~~~~~~~~~

- **DingTalk** works. Before 2.0 its schema could never validate. Send a text message with ``message='...'``, or any message
  type with ``msg_data={'msgtype': ..., <msgtype>: {...}}``.
- ``get_notifier()`` works for providers registered only via entry points.
- Importing notifiers no longer performs a hostname lookup (`#483 <https://github.com/liiight/notifiers/issues/483>`_).
  The default email ``from`` address is computed only when sending an email without a ``from`` address.
- Email / Gmail / iCloud: a single attachment path (``attachments='/path/to/file'``) works. Before 2.0 it failed with
  ``Is a directory: '/'``.

.. _migration_providers:

For custom provider authors
---------------------------

Providers and resources declare a ``schema_model`` instead of the ``_required`` and ``_schema`` dicts. Everything else stays
the same: ``_prepare_data``, ``_validate_data_dependencies`` and ``_send_notification`` still receive plain dicts.

Before:

.. code-block:: python

    from notifiers.core import Provider, Response
    from notifiers.utils.schema.helpers import one_or_more

    class MyProvider(Provider):
        name = "my_provider"
        base_url = "https://api.example.com"
        site_url = "https://example.com"

        _required = {"required": ["message", "api_key"]}
        _schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string", "title": "the message"},
                "api_key": {"type": "string", "title": "API key"},
                "to": one_or_more({"type": "string", "format": "email", "title": "recipients"}),
                "retries": {"type": "integer", "minimum": 0, "title": "retries"},
                "username": {"type": "string", "title": "username"},
                "password": {"type": "string", "title": "password"},
            },
            "dependencies": {"username": ["password"], "password": ["username"]},
            "additionalProperties": False,
        }

        @property
        def defaults(self):
            return {"retries": 3}

        def _send_notification(self, data: dict) -> Response: ...

After:

.. code-block:: python

    from pydantic import Field, model_validator

    from notifiers.core import Provider, Response
    from notifiers.models import Email, OneOrMore, SchemaModel

    class MyProviderSchema(SchemaModel):
        message: str = Field(description="the message")
        api_key: str = Field(description="API key")
        to: OneOrMore[Email] | None = Field(None, description="recipients")
        retries: int = Field(3, ge=0, description="retries")
        username: str | None = Field(None, description="username")
        password: str | None = Field(None, description="password")

        @model_validator(mode="after")
        def _credentials(self):
            self.require_dependencies({"username": ["password"], "password": ["username"]})
            return self

    class MyProvider(Provider):
        name = "my_provider"
        base_url = "https://api.example.com"
        site_url = "https://example.com"

        schema_model = MyProviderSchema

        def _send_notification(self, data: dict) -> Response: ...

How JSON schema concepts map to the model:

.. list-table::
   :header-rows: 1

   * - Before (JSON schema)
     - After (pydantic)
   * - ``_required = {"required": ["a"]}``
     - A field without a default: ``a: str``
   * - optional property
     - ``a: str | None = None``
   * - ``defaults`` property
     - A field default: ``a: int = 3``. ``provider.defaults`` is derived from them
   * - ``"title"``
     - ``Field(description=...)``
   * - ``"enum": [...]``
     - ``typing.Literal[...]``
   * - ``minimum`` / ``maximum`` / ``maxLength`` / ``minItems``
     - ``Field(ge=..., le=..., max_length=..., min_length=...)``
   * - ``one_or_more(schema)``
     - ``OneOrMore[T]``, or ``one_or_more(T, max_items=..., unique=...)``
   * - ``"format": "email"`` and the other custom formats
     - ``Email``, ``Url``, ``Port``, ``Timestamp``, ``ISO8601Datetime``, ``RFC2822Datetime``, ``DateString``, ``AsciiStr``,
       ``FilePath``, ``E164`` from :mod:`notifiers.models`
   * - ``"additionalProperties": False``
     - The default. For ``True`` set ``model_config = ConfigDict(extra="allow")``
   * - nested ``"type": "object"``
     - Another ``SchemaModel`` subclass used as the field type
   * - ``"dependencies"``, ``anyOf`` / ``oneOf`` of ``required`` and any other cross field rule
     - A pydantic ``@model_validator(mode="after")`` raising ``pydantic_core.PydanticCustomError``. ``SchemaModel`` has
       ``is_set(name)`` and ``require_dependencies({"a": ["b"]})`` helpers for the common cases
   * - ``from`` / ``from_`` duplicate properties
     - One field with an alias: ``from_: str = Field(alias="from")``. Both spellings are accepted
   * - camelCase property names, e.g. ``deviceId``
     - A snake_case field with the API name as alias: ``device_id: str = Field(alias="deviceId")``. Both spellings are
       accepted, the alias is used in the processed data

Other changes for provider authors:

- ``SchemaResource`` lost the ``validator`` attribute and the ``_validate_schema()`` method.
- ``SchemaResource._validate_data()`` returns the validated data. Arguments are keyed by their alias (``from_`` becomes
  ``from``) and values are converted to their declared types.
- ``notifiers.utils.schema`` was removed. ``list_to_commas`` moved to :func:`notifiers.utils.helpers.list_to_commas`.
