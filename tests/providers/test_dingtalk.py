import pytest

provider = "dingtalk"


class TestDingTalk:
    def test_dingtalk_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "https://oapi.dingtalk.com/robot/send?access_token={}",
            "name": "dingtalk",
            "site_url": "https://oapi.dingtalk.com/",
        }

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        msg_data = {"msgtype": "text", "text": {"content": test_message}}
        data = {"access_token": "token", "msg_data": msg_data}
        provider.notify(**data, raise_on_errors=True)
