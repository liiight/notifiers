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

2.0.0 changes the dependencies, so the formula needs editing by hand:

- ``jsonschema`` and its dependencies (``attrs``, ``jsonschema-specifications``, ``referencing``, ``rpds-py``) and
  ``importlib-metadata`` / ``zipp`` are gone
- ``pydantic`` is new. Use Homebrew's ``pydantic`` formula, which bundles ``pydantic-core`` (built from Rust) and its
  dependencies, rather than resources, like other formulae do (e.g. ``wtfis``)
- Python 3.10 or newer is required (the formula uses ``python@3.14``)
- the ``url`` and ``sha256`` change to the 2.0.0 sdist on PyPI

The 2.0.0 formula, with the placeholders filled in from PyPI. The other resources are the ones the current formula pins,
keep whichever versions are newest at release time:

.. code-block:: ruby

    class Notifiers < Formula
      include Language::Python::Virtualenv

      desc "Easy way to send notifications"
      homepage "https://notifiers.readthedocs.io/"
      url "https://files.pythonhosted.org/packages/<path>/notifiers-2.0.0.tar.gz"
      sha256 "<sha256 of notifiers-2.0.0.tar.gz>"
      license "MIT"

      depends_on "certifi" => :no_linkage
      depends_on "pydantic" => :no_linkage
      depends_on "python@3.14"

      pypi_packages exclude_packages: %w[certifi pydantic]

      resource "charset-normalizer" do
        url "https://files.pythonhosted.org/packages/33/1c/f41d4e74c28ab327ff3acd36053f7ea506c55872d7a90b0fa71aa3ab0c89/charset_normalizer-3.5.2.tar.gz"
        sha256 "39de2a259fc954455c57274dc94c79d5842774e1247a016aff30bc0efed0f4ef"
      end

      resource "click" do
        url "https://files.pythonhosted.org/packages/c7/0e/7fa0ef50764b67090eca4114772a2abf8b6148198475e54c660b97caeee6/click-8.5.0.tar.gz"
        sha256 "ba0d2089de75ea0310e2dde03160e6ca10009947fb95a182f9b54021bb272e34"
      end

      resource "idna" do
        url "https://files.pythonhosted.org/packages/f5/08/8eea9d4b8302028f3abb2c0813953f7aec26d33b7a8960ed760e65ff29fa/idna-3.20.tar.gz"
        sha256 "a7db850025b95ded1eae8a46181a1a6c56c92c96f0e2b005d9ff8dc0210cab44"
      end

      resource "requests" do
        url "https://files.pythonhosted.org/packages/ac/c3/e2a2b89f2d3e2179abd6d00ebd70bff6273f37fb3e0cc209f48b39d00cbf/requests-2.34.2.tar.gz"
        sha256 "f288924cae4e29463698d6d60bc6a4da69c89185ad1e0bcc4104f584e960b9ed"
      end

      resource "urllib3" do
        url "https://files.pythonhosted.org/packages/e3/05/b17359e1cefb4f909b5e40b1b90a496d987258916dbbf88e842c729f510e/urllib3-2.8.0.tar.gz"
        sha256 "63bf2ead4c879426ebf22ef2a781eeb4aa3b4ae798a0435506f8687fd5bb9b63"
      end

      def install
        virtualenv_install_with_resources

        generate_completions_from_executable(bin/"notifiers", shell_parameter_format: :click)
      end

      test do
        assert_match "notifiers #{version}", shell_output("#{bin}/notifiers --version")
        assert_match "pushover", shell_output("#{bin}/notifiers providers")
        assert_match "'to' is a required property", shell_output("#{bin}/notifiers email notify hi 2>&1", 1)
      end
    end

``brew update-python-resources notifiers`` regenerates the resource list from PyPI, and ``brew audit --strict --new
notifiers`` and ``brew test notifiers`` check the formula before opening the pull request on homebrew-core.
