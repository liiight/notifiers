Command Line Interface
----------------------

Notifiers come with CLI support

Main view
=========

To view the main help just enter ``notifiers`` or ``notifiers --help``:

.. code-block:: console

    $ notifiers
    Usage: notifiers [OPTIONS] COMMAND [ARGS]...

      Notifiers CLI operation

    Options:
     --version          Show the version and exit.
     --env-prefix TEXT  Set a custom prefix for env vars usage
     --help             Show this message and exit.


    Commands:
      email       Options for 'email'
      gitter      Options for 'gitter'
      gmail       Options for 'gmail'
      join        Options for 'join'
      providers   Shows all available providers
      pushbullet  Options for 'pushbullet'
      pushover    Options for 'pushover'
      simplepush  Options for 'simplepush'
      slack       Options for 'slack'
      telegram    Options for 'telegram'
      zulip       Options for 'zulip'
      victorops       Options for 'victorops'
      notify      Options for 'notify'


To view all providers use the ``providers`` command like so:

.. code-block:: console

     $ notifiers providers
     pushover, simplepush, slack, email, gmail, telegram, gitter, pushbullet, join, zulip, victorops

This will return all available provider names

Provider actions
================

Each provider has a group of actions it can perform. Due to the generic nature that providers are implemented in, these actions are usually shared among all providers. To access available commands, use the ``notifiers [PROVIDER_NAME] --help`` command:

.. code-block:: console

    $ notifiers email --help
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

The ``defaults``, ``metadata``, ``required`` and ``schema`` command all return a JSON output of the relevant provider property:

.. code-block:: console

    $ notifiers email metadata
    {"base_url": null, "site_url": "https://en.wikipedia.org/wiki/Email", "provider_name": "email"}

These helper methods can also accept a ``--pretty`` flag which will out a nicely indented JSON:

.. code-block:: console

    $ notifiers email metadata --pretty
    {
        "base_url": null,
        "site_url": "https://en.wikipedia.org/wiki/Email",
        "provider_name": "email"
    }

Sending a notification
======================
To send a notification you use the ``notify`` command. Each notifier has its own set of relevant options it can take. View them by sending the ``notifiers [PROVIDER_NAME] notify --help``:

.. code-block:: console

    $ notifiers email notify --help
    Usage: notifiers email notify [OPTIONS] [MESSAGE]

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

.. note::

   Due to the nature of command line syntax, only primitive argument types can be used with it, meaning you can only pass string, int, float and booleans (using flags) when invoking the notify command via CLI. List and dict arguments cannot be passed with it.

Note that ``message`` is an expected argument that need to be either explicitly set or piped into the command.

Piping into a notification
==========================
Notifiers CLI enable using pipe to directly pass value to the ``message`` argument:

.. code-block:: console

    $ cat file.txt | notifiers notify email --to blah@foo.com

Environment variables
=====================

:ref:`environs` are respected by all means of notification by notifiers and the CLI is no different to that aspect.
If you defined for example ``NOTIFIERS_PUSHOVER_TOKEN`` and ``NOTIFIERS_PUSHOVER_USER`` you can simply run:

.. code-block:: console

    $ export NOTIFIERS_PUSHOVER_TOKEN=FOO
    $ export NOTIFIERS_PUSHOVER_USER=BAR
    $ notifiers notify pushover "wow, this is easy!"

You can change the default env var prefix (which is ``NOTIFIERS_``) by sending the ``--env-prefix`` option:

.. code-block:: console

   $ notifiers --env-prefix FOO_ notify pushover "Yep, easy stuff!"

.. note::

   You can create a convenience alias for your used provider to even simplify this further:

   .. code-block:: console

        $ alias notify="notifiers notify pushover"

   And when combining this with setting environment variables, you can run:

   .. code-block:: console

        $ notify "this is even easier!"

Provider resources
==================

Some providers have resource helper commands:

.. code-block:: console

    $ notifiers telegram resources
    updates

You can also see them in the provider ``--help`` view:

.. code-block:: console

    $ notifiers telegram --help
    Usage: notifiers telegram [OPTIONS] COMMAND [ARGS]...

      Options for 'telegram'

    Options:
      --help  Show this message and exit.

    Commands:
      defaults   'telegram' default values
      metadata   'telegram' metadata
      notify     Send Telegram notifications
      required   'telegram' required schema
      resources  Show provider resources list
      schema     'telegram' full schema
      updates    Return Telegram bot updates, correlating to...

These resources have their own option they can use:

.. code-block:: console

    $ notifiers telegram updates --help
    Usage: notifiers telegram updates [OPTIONS]

      Return Telegram bot updates, correlating to the `getUpdates` method.
      Returns chat IDs needed to notifications

    Options:
      --token TEXT             Bot token
      --pretty / --not-pretty  Output a pretty version of the JSON
      --help                   Show this message and exit.

Invoking them returns a JSON reply (usually), where each reply correlates to the API data.

.. note::
   Like always, these resources play very nicely with environment variables, so if you set your token in an environment variable, the resource can pick that up by default


Version
=======
Get installed ``notifiers`` version via the ``--version`` flag:

.. code-block:: console

    $ notifiers --version
    notifiers 0.6.3

