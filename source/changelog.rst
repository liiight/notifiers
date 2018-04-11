Changelog
=========

Unreleased (develop)
--------------------

Added
~~~~~

- Added ability to add email attachment via SMTP (`#91 <https://github.com/liiight/notifiers/pull/91>`_) via (`#99 <https://github.com/liiight/notifiers/pull/99>`_). Thanks `@grabear <https://github.com/grabear>`_

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
