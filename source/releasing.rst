.. _releasing:

Releasing
=========

Steps for maintainers to publish a new version.

1. Prepare
----------

- Set the version in ``pyproject.toml`` and ``notifiers/_version.py``.
- Date the version heading in ``source/changelog.rst``, e.g. ``2.0.0 (2026-10-12)``.
- Merge to ``main`` and wait for CI to pass.

2. Tag and publish
------------------

.. code-block:: console

    $ git tag v2.0.0 && git push origin v2.0.0
    $ uv build
    $ uv publish

The tag:

- publishes the Docker image ``ghcr.io/liiight/notifiers`` as ``2.0.0``, ``2.0`` and ``latest`` (``.github/workflows/docker.yml``)
- moves the ``stable`` version of the documentation on Read the Docs to the new tag

Optionally create a GitHub release with the changelog entry as the release notes:

.. code-block:: console

    $ gh release create v2.0.0 --title "2.0.0" --notes "See https://notifiers.readthedocs.io/en/stable/changelog.html"

3. Homebrew
-----------

The formula is maintained in `Homebrew/homebrew-core <https://github.com/Homebrew/homebrew-core/blob/main/Formula/n/notifiers.rb>`_
and installs the source distribution from PyPI, so it can only be updated after ``uv publish``.

For releases that don't change the dependencies, ``brew bump-formula-pr`` updates the formula and opens the pull request
on homebrew-core:

.. code-block:: console

    $ brew bump-formula-pr --url "https://files.pythonhosted.org/packages/.../notifiers-X.Y.Z.tar.gz" notifiers

Homebrew's autobump also opens these pull requests by itself shortly after a release.

The formula is kept in this repository as ``packaging/homebrew/notifiers.rb``, and CI installs this repository's code
with it on macOS and Linux (``.github/workflows/homebrew.yml``): it builds the sdist, installs it with
``brew install --build-from-source``, and runs ``brew test`` and ``brew audit --strict``. It also checks that the
formula's resources are exactly the runtime dependencies that aren't Homebrew formulae
(``packaging/homebrew/check_formula.py``). Keep the file in sync when the dependencies change, e.g. with
``brew update-python-resources``.

To update the formula on homebrew-core after a release, copy ``packaging/homebrew/notifiers.rb`` over
``Formula/n/notifiers.rb`` in a homebrew-core checkout, set ``url`` and ``sha256`` to the sdist on PyPI, then run
``brew audit --strict --online notifiers`` and ``brew test notifiers`` and open the pull request.

Compared to the formula for 1.3.6, the formula for 2.0.0:

- drops ``jsonschema`` and its dependencies (``attrs``, ``jsonschema-specifications``, ``referencing``, ``rpds-py``) and
  ``importlib-metadata`` / ``zipp``
- depends on Homebrew's ``pydantic`` formula, which bundles ``pydantic-core`` (built from Rust) and its dependencies,
  instead of resources, like other formulae do (e.g. ``wtfis``)
- tests ``--version``, ``providers`` and a validation error, not just ``--help``
