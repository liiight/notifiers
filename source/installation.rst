.. _installation:

Installation
------------

.. note:: Python 3.10 or newer is required.

As a library
============
Add notifiers to your project with `uv <https://docs.astral.sh/uv/>`_:

.. code-block:: console

    $ uv add notifiers

Or install from source:

.. code-block:: console

    $ uv add git+https://github.com/liiight/notifiers --branch main

As a command line tool
======================
Run the CLI with ``uvx``, without installing anything:

.. code-block:: console

    $ uvx notifiers --help
    $ uvx notifiers pushover notify --user foo --token baz "Hello"

Or install the ``notifiers`` command once, in its own isolated environment:

.. code-block:: console

    $ uv tool install notifiers
    $ notifiers --help

To run the latest code from the ``main`` branch:

.. code-block:: console

    $ uvx --from git+https://github.com/liiight/notifiers@main notifiers --help

Via pip
=======
You can also install via pip:

.. code-block:: console

    $ pip install notifiers

Via homebrew
============
Installs the CLI, with shell completions:

.. code-block:: console

    $ brew install notifiers

The `formula <https://github.com/Homebrew/homebrew-core/blob/main/Formula/n/notifiers.rb>`_ is maintained in
homebrew-core and updated to new releases after they're published to PyPI.

Via docker
==========
The CLI is also published as a Docker image on the
`GitHub Container Registry <https://github.com/liiight/notifiers/pkgs/container/notifiers>`_, for ``linux/amd64`` and
``linux/arm64``. Its entry point is the ``notifiers`` command:

.. code-block:: console

    $ docker run --rm ghcr.io/liiight/notifiers --version
    $ docker run --rm ghcr.io/liiight/notifiers pushover notify --user foo --token baz "Hello"

Environment variables and piped messages work as with the installed CLI:

.. code-block:: console

    $ echo "Hello" | docker run --rm -i -e NOTIFIERS_PUSHOVER_USER=foo -e NOTIFIERS_PUSHOVER_TOKEN=baz ghcr.io/liiight/notifiers pushover notify

Image tags:

- ``latest`` and ``<version>`` (e.g. ``2.0.0``, ``2.0``): released versions
- ``main``: the latest code on the ``main`` branch

To build the image locally:

.. code-block:: console

    $ docker buildx bake
