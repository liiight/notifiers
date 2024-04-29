import pytest

provider = "notify"


class TestNotify:
    """
    Notify notifier tests
    """

    @pytest.mark.online
    def test_notify_sanity(self, provider, test_message):
        """Successful notify notification"""
        data = {
            "message": test_message,
            "title": "test",
            "base_url": "https://notify-demo.deno.dev",
            "tags": ["test"],
            "token": "mypassword",
        }

        rsp = provider.notify(**data)
        rsp.raise_on_errors()
