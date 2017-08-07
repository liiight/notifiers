Notifiers
=========

The easiest way to send push notifications!

.. image:: https://img.shields.io/travis/liiight/notifiers/master.svg
:target: https://travis-ci.org/liiight/notifiers

.. image:: https://codecov.io/gh/liiight/notifiers/branch/master/graph/badge.svg
:target: https://codecov.io/gh/liiight/notifiers

.. image:: https://img.shields.io/gitter/room/nwjs/nw.js.svg
:target: https://gitter.im/notifiers/notifiers


From python:

.. code:: python

    >>> from notifiers import get_notifier

    >>> pushover = get_notifer('pushover')
    >>> pushover.notify(title='Foo', message='Bar', token='TOKEN')

Setup
-----
Install with pip::

    pip install notifiers

Usage
-----

Get a notifier:

.. code:: python

    pushover = notifiers.get_notifer('pushover')

Or:

.. code:: python

    pushover = notifiers.providers.Pushover()

Send a notification:

.. code:: python

    pushover.notify(token='TOKEN', title='Foo', message='Bar')

Get notifier metadata:

.. code:: text

    print(pushover.metadata)

    {
        "url": "http://..."
        "description": "A Great notifier!"
        ..
    }

In the near future
------------------

-  Many more providers
-  CLI
-  Environment variable support
-  Docs

Why python 3 only?
~~~~~~~~~~~~~~~~~~

I wanted to avoid the whole unicode issue fiasco if possible, but
there’s not real constraint in adding python 2 support. If there’s an
overwhelming desire for this, i’ll do it. Probably.

