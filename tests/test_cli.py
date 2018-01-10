import re

import pytest
from click.testing import CliRunner

from notifiers import __version__

mock_name = 'mock_provider'


@pytest.mark.usefixtures('mock_provider', 'load_cli_providers')
class TestCLI:
    """CLI tests"""

    @pytest.mark.parametrize('command, exit_code, error', [
        ('', 2, 'Got unexpected extra argument'),
    ])
    def test_bad_notify(self, command, exit_code, error, notifiers_cli_main):
        """Test invalid notification usage"""
        runner = CliRunner()

        result = runner.invoke(notifiers_cli_main, [mock_name, 'notify', command])
        assert result.exit_code == exit_code
        assert error in result.output

    def test_notify_sanity(self, notifiers_cli_main):
        """Test valid notification usage"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'notify', '--message', 'foo', '--required', 'bar'])
        assert result.exit_code == 0
        assert not result.output

    def test_providers(self, notifiers_cli_main):
        """Test providers command"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, ['providers'])
        assert result.exit_code == 0
        assert 'mock' in result.output

    def test_metadata(self, notifiers_cli_main):
        """Test metadata command"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'metadata'])
        assert result.exit_code == 0
        assert '"base_url": "https://api.mock.com"' in result.output
        assert '"site_url": "https://www.mock.com"' in result.output
        assert '"provider_name": "mock_provider"' in result.output

    def test_required(self, notifiers_cli_main):
        """Test required command"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'required'])
        assert result.exit_code == 0
        assert 'required' in result.output

    def test_help(self, notifiers_cli_main):
        """Test help command"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'notify', '--help'])
        assert result.exit_code == 0
        assert '--required' in result.output
        assert '--not-required' in result.output
        assert '--message' in result.output

    def test_no_defaults(self, notifiers_cli_main):
        """Test defaults command"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, ['pushover', 'defaults'])
        assert result.exit_code == 0
        assert '{}' in result.output

    def test_defaults(self, notifiers_cli_main):
        """Test defaults command"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'defaults'])
        assert result.exit_code == 0
        assert '"option_with_default": "foo"' in result.output

    def test_piping_input(self, notifiers_cli_main):
        """Test piping in message"""
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'notify', '--required', 'foo'], input='bar')
        assert result.exit_code == 0
        assert not result.output

    def test_environ(self, monkeypatch, notifiers_cli_main):
        """Test provider environ usage """
        monkeypatch.setenv('NOTIFIERS_MOCK_PROVIDER_REQUIRED', 'foo')
        monkeypatch.setenv('NOTIFIERS_MOCK_PROVIDER_MESSAGE', 'foo')
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, [mock_name, 'notify'])
        assert result.exit_code == 0
        assert not result.output

    def test_version_command(self, notifiers_cli_main):
        runner = CliRunner()
        result = runner.invoke(notifiers_cli_main, ['--version'])
        assert result.exit_code == 0
        version_re = re.search('(\d+\.\d+\.\d+)', result.output)
        assert version_re
        assert version_re.group(1) == __version__
