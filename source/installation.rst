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

.. code-block:: console

    $ brew install notifiers

Via docker
==========
Alternatively, use DockerHub:

.. code-block:: console

    $ docker pull liiight/notifiers

Or build from ``Dockerfile`` locally
