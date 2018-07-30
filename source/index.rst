.. notifiers documentation master file, created by
   sphinx-quickstart on Thu Aug 10 18:14:08 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Notifiers documentation!
=====================================

Got an app or service and you want to enable your users to use notifications with their provider of choice? Working on a script and you want to receive notification based on its output? You don't need to implement a solution yourself, or use individual provider libs. A one stop shop for all notification providers with a unified and simple interface.

Click for a list of currently supported :ref:`providers`

Advantages
----------
- Spend your precious time on your own code base, instead of chasing down 3rd party provider APIs. That's what we're here for!
- With a minimal set of well known and stable dependencies (`requests <https://pypi.python.org/pypi/requests>`_, `jsonschema <https://pypi.python.org/pypi/jsonschema/2.6.0>`_ and `click <https://pypi.python.org/pypi/click/6.7>`_) you're better off than installing 3rd party SDKs.
- A unified interface means that you already support any new providers that will be added, no more work needed!
- Thorough testing means protection against any breaking API changes. We make sure your code your notifications will always get delivered!

Installation
------------
Via pip:

.. code-block:: console

    $ pip install notifiers

Or Dockerhub:

.. code-block:: console

    $ docker pull liiight/notifiers


Basic Usage
-----------

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> p = get_notifier('pushover')
    >>> p.required
    {'required': ['user', 'message', 'token']}
    >>> p.notify(user='foo', token='bar', message='test')
    <NotificationResponse,provider=Pushover,status=Success>

From CLI
--------

.. code-block:: console

    $ notifiers pushover notify --user foo --token baz "This is so easy!"

As a logger
-----------

Directly add to your existing stdlib logging:

.. code-block:: python

    >>> import logging
    >>> from notifiers.logging import NotificationHandler
    >>> log = logging.getLogger(__name__)
    >>> defaults = {
            'token': 'foo,
            'user': 'bar
        }
    >>> hdlr = NotificationHandler('pushover', defaults=defaults)
    >>> hdlr.setLevel(logging.ERROR)
    >>> log.addHandler(hdlr)
    >>> log.error('And just like that, you get notified about all your errors!')

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   changelog
   about
   installation
   usage
   CLI
   Logger

Providers documentation
-----------------------

.. toctree::

  providers/index

API documentation
-----------------

.. toctree::

   api/index

Development documentation
-------------------------
TBD

Donations
---------

If you like this and want to buy me a cup of coffee, please click the donation button above or click this `link <https://paypal.me/notifiers>`_ ☕


**Indices and tables**

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`