Command Line Interface
----------------------

.. warning:: This API is subject to slightly change in an upcoming release

Notifiers come with CLI support::

    (notifiers_venv) ip-192-168-1-169:notifiers $ notifiers
    Usage: notifiers [OPTIONS] COMMAND [ARGS]...

      Notifiers CLI operation

    Options:
      --help  Show this message and exit.

    Commands:
      arguments  Shows the name and schema of all the...
      defaults   Shows the provider's defaults.
      metadata   Shows the provider's metadata.
      notify     Send a notification to a passed provider.
      providers  Shows all available providers
      required   Shows the required attributes of a provider.

Because of the dynamic nature of using different provider options, those are passed in a keyword=value style to the command as so::

    $ notifiers notify pushover token=foo user=bar message=test

Environment variables are used in the CLI as well. Explicitly passing keyword values takes precedence.
You can also pipe into the command::

    $ cat file.txt | notifiers notify pushover token=foo user=bar

You can set ``NOTIFIERS_DEFAULT_PROVIDER`` environment variable which will be used by the CLI. Combining that with the other required provider arguments can lead to very succinct commands::

    $ cat file.txt | notifiers notify

Note that unlike the other environment variables, you cannot change the prefix of this one.

Get installed ``notifiers`` version via the ``--version`` flag::

    $ notifiers --version
    notifiers 0.6.3
