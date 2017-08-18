import pytest

from click.testing import CliRunner


class TestCLI(object):
    """CLI tests"""

    @pytest.mark.parametrize('command, exit_code, error', [
        ('', 2, 'invalid choice'),
        ('mock', 1, 'Error with sent data')
    ])
    def test_bad_notify(self, command, exit_code, error,
                        mock_provider):
        """Test invalid notification usage"""
        from notifiers_cli.cli import notify
        mock_provider()
        runner = CliRunner()

        result = runner.invoke(notify, [command])
        assert result.exit_code == exit_code
        assert error in result.output

    def test_notify_sanity(self):
        """Test valid notification usage"""

    def test_providers(self):
        """Test providers command"""

    def test_metadata(self):
        """Test metadata command"""

    def test_required(self):
        """Test metadata command"""

    def test_arguments(self):
        """Test metadata command"""
