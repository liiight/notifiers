# Issues

Please describe the issue, add relevant errors/crash and specify exact python version, notifiers version and installation method (pip, docker, from source, etc.)

# Pull requests and Development

Detailed developmental docs are planned but for the meanwhile this is the bare minimum:

- Fork repo.
- Install requirements via `pip install -r requirements.txt`
- Install dev requirements via  `pip install -r dev-requirements.txt`
- Run tests via `pytest -m "not online"`

## Tests

When adding new functionality, please add new tests to it. If new account and/or secret keys are needed to be created and added to the repo, please reach out via [gitter](https://gitter.im/notifiers/notifiers).

There are 3 types of tests:

- "Dry" tests, tests that check the code base directly without needing 3rd party providers.
- "Wet" tests, tests that do require 3rd party providers but are negative tests, or expected to fail. They can pass even without passing the required credentials to them.
- "Online" tests, tests that require real API access to the various providers. Any secret information that is needed to to make these test pass is encrypted via CI settings and is accessible only to owners of the project. When running tests locally run via the negative marker as written above. When a pull request is created, these tests are skipped.

Skipping these tests will have the appearance that the test coverage dropped considerably (becuase for the scope of this PR, it did). Feel free to ignore this.