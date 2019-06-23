.. _changelog:

Changelog
=========

1.2.0 (Unreleased)
------------------

- Added ability to cancel login to SMTP/GMAIL if credentials are used (`#210 <https://github.com/notifiers/notifiers/issues/210>`_, `#266 <https://github.com/notifiers/notifiers/pull/266>`_)
- Loosened dependencies (`#209 <https://github.com/notifiers/notifiers/issues/209>`_, `#266 <https://github.com/notifiers/notifiers/pull/271>`_)
- Added mimetype guessing for email (`#239 <https://github.com/notifiers/notifiers/issues/239>`_, `#266 <https://github.com/notifiers/notifiers/pull/271>`_)


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
