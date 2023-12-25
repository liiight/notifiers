import pytest

provider = "notify"


class TestNotify:
    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {"message": test_message}
        provider.notify(**data, raise_on_errors=True)
