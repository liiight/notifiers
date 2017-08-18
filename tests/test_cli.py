import pytest

from click.testing import CliRunner


@pytest.mark.usefixtures('mock_provider')
class TestCLI(object):
    """CLI tests"""

    @pytest.mark.parametrize('command, exit_code, error', [
        ('', 2, 'invalid choice'),
        ('mock', 1, 'Error with sent data')
    ])
    def test_bad_notify(self, command, exit_code, error):
        """Test invalid notification usage"""
        from notifiers_cli.cli import notify
        runner = CliRunner()

        result = runner.invoke(notify, [command])
        assert result.exit_code == exit_code
        assert error in result.output

    def test_notify_sanity(self):
        """Test valid notification usage"""
        from notifiers_cli.cli import notify
        runner = CliRunner()
        result = runner.invoke(notify, ['mock', 'required=foo'])
        assert result.exit_code == 0
        assert not result.output

    def test_providers(self, ):
        """Test providers command"""
        from notifiers_cli.cli import providers
        runner = CliRunner()
        result = runner.invoke(providers, [])
        assert result.exit_code == 0
        assert 'mock' in result.output

    def test_metadata(self):
        """Test metadata command"""
        from notifiers_cli.cli import metadata
        runner = CliRunner()
        result = runner.invoke(metadata, ['mock'])
        assert result.exit_code == 0
        assert "base_url: https://api.mock.com" in result.output
        assert "site_url: https://www.mock.com" in result.output
        assert "provider_name: mock_provide" in result.output

    def test_required(self):
        """Test metadata command"""
        from notifiers_cli.cli import required
        runner = CliRunner()
        result = runner.invoke(required, ['mock'])
        assert result.exit_code == 0
        assert 'required' in result.output

    def test_arguments(self):
        """Test metadata command"""
        from notifiers_cli.cli import arguments
        runner = CliRunner()
        result = runner.invoke(arguments, ['mock'])
        assert result.exit_code == 0
        assert 'required' in result.output
        assert 'not_required' in result.output
        assert 'message' in result.output
