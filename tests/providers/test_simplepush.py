import pytest

provider = "simplepush"


class TestSimplePush:
    """SimplePush notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_SIMPLEPUSH_KEY
    """

    @pytest.mark.online
    def test_simplepush_sanity(self, provider, test_message):
        """Successful simplepush notification"""
        data = {"message": test_message}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()
