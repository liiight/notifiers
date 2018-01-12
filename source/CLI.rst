Command Line Interface
----------------------

Notifiers come with CLI support

Main view
=========

To view the main help just enter ``notifier`` or ``notifiers --help``::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers
    Usage: notifiers [OPTIONS] COMMAND [ARGS]...

      Notifiers CLI operation

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      email       Options for 'email'
      gitter      Options for 'gitter'
      gmail       Options for 'gmail'
      hipchat     Options for 'hipchat'
      join        Options for 'join'
      providers   Shows all available providers
      pushbullet  Options for 'pushbullet'
      pushover    Options for 'pushover'
      simplepush  Options for 'simplepush'
      slack       Options for 'slack'
      telegram    Options for 'telegram'
      zulip       Options for 'zulip'


To view all providers use the ``providers`` command like so::

        (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers providers
        pushover, simplepush, slack, email, gmail, telegram, gitter, pushbullet, join, hipchat, zulip

This will return all available provider names

Provider groups
===============

Each provider correlates to a group of actions it can perform. Due to the generic nature that providers are implemented in, these actions are usually shared among all providers. To access available commands, use the ``notifiers [PROVIDER_NAME] --help`` command::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers email --help
    Usage: notifiers email [OPTIONS] COMMAND [ARGS]...

      Options for 'email'

    Options:
      --help  Show this message and exit.

    Commands:
      defaults  'email' default values
      metadata  'email' metadata
      notify    Send emails via SMTP
      required  'email' required schema
      schema    'email' full schema

The ``defaults``, ``metadata``, ``required`` and ``schema`` command all return a JSON dump of the relevant provider property::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers email metadata
    {"base_url": null, "site_url": "https://en.wikipedia.org/wiki/Email", "provider_name": "email"}

These helper method can also accept a ``--pretty`` flag which will out a nicely indented JSON::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers email metadata
    {
        "base_url": null,
        "site_url": "https://en.wikipedia.org/wiki/Email",
        "provider_name": "email"
    }

Sending a notification
======================
To send a notification you use the ``notify`` command. Each notifier has its own set of relevant options it can take. View them by sending the ``notifiers [PROVIDER_NAME] notify --help``::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers email notify --help
    Usage: core.py email notify [OPTIONS] [MESSAGE]

      Send emails via SMTP

    Options:
      --subject TEXT      The subject of the email message
      --to TEXT           One or more email addresses to use. Multiple usages of
                          this option are allowed
      --from TEXT         The from address to use in the email
      --host TEXT         The host of the smtp server
      --port INTEGER      The port number to use
      --username TEXT     Username if relevant
      --password TEXT     Password if relevant
      --tls / --no-tls    Should tls be used
      --ssl / --no-ssl    Should ssl be used
      --html / --no-html  Should the email be parse as an html file
      --help              Show this message and exit.


Note that ``message`` is an expected argument that need to be either explicitly passed in.

Piping into a notification
==========================
Notifiers CLI enable using pipe to directly pass value to the ``message`` argument::

    cat file.txt | notifiers notify email --to blah@foo.com

Environment variables
=====================

Environment variables are respected by all means of notification by :mod:`notifiers` and the CLI is no different to that aspect.
If you defined for example ``NOTIFIERS_PUSHOVER_TOKEN`` and ``NOTIFIERS_PUSHOVER_USER`` you can simply run::

    notifiers notify pushover "wow, this is easy!"

.. note::

   You can create a convinence alias for your used provider to even simplify this further::

        alias not="notifiers notify pushover"

   Then just use::

        not "this is even easier!"

Version
=======
Get installed ``notifiers`` version via the ``--version`` flag:

    $ notifiers --version
    notifiers 0.6.3

