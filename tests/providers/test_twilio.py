import pytest

provider = "twilio"


class TestTwilio:
    def test_twilio_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json",
            "name": "twilio",
            "site_url": "https://www.twilio.com/",
        }

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {"message": test_message}
        provider.notify(**data, raise_on_errors=True)
