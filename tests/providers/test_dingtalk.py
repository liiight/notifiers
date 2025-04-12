import pytest

provider = "dingtalk"


class TestDingTalk:
    def test_dingtalk_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "https://oapi.dingtalk.com/robot/send",
            "name": "dingtalk",
            "site_url": "https://oapi.dingtalk.com/",
        }

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {"access_token": "token", "message": test_message}
        provider.notify(**data, raise_on_errors=True)
