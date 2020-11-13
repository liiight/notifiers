import pytest

provider = "twilio"


class TestTwilio:
    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {"message": test_message}
        provider.notify(**data, raise_on_errors=True)
