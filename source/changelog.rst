.. _changelog:

Changelog
=========

2.0.0 (unreleased)
------------------

Provider schemas are now `pydantic <https://docs.pydantic.dev/>`_ (v2) models instead of JSON Schema dicts
validated with ``jsonschema``. The public library API (``notify()``, ``get_notifier()``, ``Provider.notify()``,
``Response``, exceptions, environment variables and the logging handler) is unchanged. See :ref:`migration_2_0`
for details and for how to port custom providers.

Breaking changes
~~~~~~~~~~~~~~~~

- Dropped support for Python 3.8 and 3.9. Python 3.10+ is required.
- Replaced the ``jsonschema`` dependency with ``pydantic>=2.7,<3``.
- Custom providers declare their arguments with a ``schema_model`` (a :class:`~notifiers.models.SchemaModel` subclass)
  instead of the ``_required`` and ``_schema`` dicts. Providers that still define ``_required`` / ``_schema`` can't be
  instantiated. See :ref:`migration_providers`.
- Removed ``notifiers.utils.schema`` (``one_or_more``, ``list_to_commas`` and the ``format_checker`` with its ``is_*``
  format checks). ``list_to_commas`` moved to ``notifiers.utils.helpers``, the format checks are replaced by the types in
  :mod:`notifiers.models`.
- Removed ``SchemaResource.validator`` and ``SchemaResource._validate_schema()``. ``SchemaError`` is no longer raised.
- ``SchemaResource._validate_data()`` returns the validated data instead of ``None``.

Changes
~~~~~~~

- Argument values are converted to their declared type when possible, e.g. ``port="587"`` becomes ``587``. This makes
  environment variables usable for integer and boolean arguments.
- Arguments with an alternative spelling (``from`` / ``from_``, ``type`` / ``type_``) can also be set via environment
  variables using either spelling.
- Validation error messages for anything other than missing or unknown arguments and provider specific rules use pydantic's
  wording, e.g. ``'priority': Input should be less than or equal to 2``.
- Added ``BadArguments.errors``: a list of all validation errors (``loc``, ``msg`` and ``type`` for each).
- ``provider.schema`` returns pydantic's ``model_json_schema(by_alias=True)`` of the schema model, and
  ``provider.arguments`` its ``properties``. The layout follows pydantic (``description`` and ``title`` per argument,
  optional arguments as ``anyOf`` with ``null``, nested models under ``$defs``).
- ``provider.required`` lists the required arguments only. Conditional requirements (``anyOf`` / ``oneOf`` /
  ``dependencies``) are enforced on validation but no longer listed.
- ``provider.defaults`` is derived from the defaults declared on the schema model.
- Schema model fields are snake_case. Arguments named differently by the remote API keep that name as an alias, so both
  spellings are accepted (e.g. Join ``deviceId`` / ``device_id``, ``smsnumber`` / ``sms_number``; DingTalk ``msgtype`` /
  ``msg_type``, ``atMobiles`` / ``at_mobiles``).
- Added :mod:`notifiers.models`: the ``SchemaModel`` base class, ``OneOrMore`` / ``one_or_more`` and field types
  (``Email``, ``Url``, ``Hostname``, ``Port``, ``Timestamp``, ``ISO8601Datetime``, ``RFC2822Datetime``, ``DateString``,
  ``AsciiStr``, ``FilePath``, ``E164``).
- Importing notifiers (or any non email provider) no longer performs a hostname lookup via ``socket.getfqdn()``, which
  could block for seconds depending on the system resolver
  (`#483 <https://github.com/liiight/notifiers/issues/483>`_). The default email ``from`` address
  (``notifiers@<hostname>``) is computed only when sending an email without a ``from`` address, via
  ``notifiers.providers.email.default_from()``. Replaces the ``DEFAULT_FROM`` constant.

Fixes
~~~~~

- DingTalk: the schema could never validate and sending failed. Rewritten with nested models. Send a text message with
  ``message='...'`` or any message type with ``msg_data``.
- ``get_notifier()`` failed for providers registered only via the ``notifiers`` entry point.
- Email / Gmail / iCloud: a single attachment path (``attachments='/path/to/file'``) failed with
  ``Is a directory: '/'``.
- Documentation: the custom provider guide used APIs that don't exist (``notifiers.utils.schema.one_of``, ``_notify``).

Development
~~~~~~~~~~~

- Tests: added ``tests/test_schema_types.py`` (replaces ``tests/test_json_schema.py``),
  ``tests/providers/test_generic_provider_tests.py`` (checks every provider and resource, including snake_case field
  names) and ``tests/providers/test_email_offline.py`` (email, Gmail and iCloud end to end against a fake SMTP server).
- CI runs the offline test suite (``-m "not online"``) on every Python version (``fail-fast: false``), plus a ruff lint and
  format check. Tests that need network access are marked ``online``.
- ruff 0.16.10 in pre-commit and in the dev dependency group.
- Offline tests run without ``NOTIFIERS_*`` credentials in the environment, so they behave the same locally and in CI.
- The statuspage incident cleanup runs for online tests only, and tolerates API errors.

1.3.0
------

- Removed HipChat (`#404 <https://github.com/liiight/notifiers/pull/404>`_)
- Added VictorOps (`#401 <https://github.com/liiight/notifiers/pull/401>`_)
- Added iCloud (`#412 <https://github.com/liiight/notifiers/pull/412>`_)
- Drop Python 3.6 support

1.2.1
------------

- Adds a default timeout of (5, 20) seconds for all HTTP requests. (`#388 <https://github.com/liiight/notifiers/pull/388>`_)

1.2.0
-----

- Added ability to cancel login to SMTP/GMAIL if credentials are used (`#210 <https://github.com/notifiers/notifiers/issues/210>`_, `#266 <https://github.com/notifiers/notifiers/pull/266>`_)
- Loosened dependencies (`#209 <https://github.com/notifiers/notifiers/issues/209>`_, `#271 <https://github.com/notifiers/notifiers/pull/271>`_)
- Added mimetype guessing for email (`#239 <https://github.com/notifiers/notifiers/issues/239>`_, `#272 <https://github.com/notifiers/notifiers/pull/272>`_)


1.0.4
------

- Added `black <https://github.com/ambv/black>`_ and `pre-commit <https://pre-commit.com/>`_
- Updated deps

1.0.0
-----

- Added JSON Schema formatter support (`#107 <https://github.com/liiight/notifiers/pull/107>`_)
- Improved documentation across the board

0.7.4
-----

Maintenance release, broke markdown on pypi

0.7.3
-----

Added
~~~~~

- Added ability to add email attachment via SMTP (`#91 <https://github.com/liiight/notifiers/pull/91>`_) via (`#99 <https://github.com/liiight/notifiers/pull/99>`_). Thanks `@grabear <https://github.com/grabear>`_
- Added direct notify ability via :meth:`notifiers.core.notify` via (`#101 <https://github.com/liiight/notifiers/pull/101>`_).

0.7.2
-----

Added
~~~~~

- `Mailgun <https://www.mailgun.com/>`_ support (`#96 <https://github.com/liiight/notifiers/pull/96>`_)
- `PopcornNotify <https://popcornnotify.com/>`_ support (`#97 <https://github.com/liiight/notifiers/pull/97>`_)
- `StatusPage.io <https://statuspage.io>`_ support (`#98 <https://github.com/liiight/notifiers/pull/98>`_)

Dependency changes
~~~~~~~~~~~~~~~~~~

- Removed :mod:`requests-toolbelt` (it wasn't actually needed, :mod:`requests` was sufficient)

0.7.1
-----

Maintenance release (added logo and donation link)

0.7.0
-----

Added
~~~~~

- `Pagerduty <https://www.pagerduty.com>`_ support (`#95 <https://github.com/liiight/notifiers/pull/95>`_)
- `Twilio <https://www.twilio.com/>`_ support (`#93 <https://github.com/liiight/notifiers/pull/93>`_)
- Added :ref:`notification_logger`

**Note** - For earlier changes please see `Github releases <https://github.com/liiight/notifiers/releases>`_
