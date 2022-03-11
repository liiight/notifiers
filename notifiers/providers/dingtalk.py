from ..core import Provider
from ..core import Response
from ..utils import requests

class DingTalk(Provider):
    """Send DingTalk notifications via Robot Webhook"""
    base_url = "https://oapi.dingtalk.com/robot/send"
    site_url = "https://open.dingtalk.com/document/"
    name = "dingtalk"
    path_to_errors = ("errmsg",)

    _required = {
        "required": ["access_token", "msg_data"],
        "oneOf": [
            {"required": ["msg_data.text"]},
            {"required": ["msg_data.markdown"]},
            {"required": ["msg_data.link"]},
            {"required": ["msg_data.actionCard"]}
        ]
    }

    _schema = {
        # ... 保持之前的 schema 定义不变 ...
    }

    def _prepare_url(self) -> str:
        """返回基础URL，access_token将作为查询参数传递"""
        return self.base_url

    def _prepare_data(self, data: dict) -> dict:
        """
        Construct payload according to:
        https://open.dingtalk.com/document/orgapp-server/custom-robot-access
        """
        payload = {"msgtype": data["msg_data"]["msgtype"]}
        
        # Handle different message types
        msg_type = data["msg_data"]["msgtype"]
        payload[msg_type] = data["msg_data"].get(msg_type, {})
        
        # Handle @ mentions
        if "at" in data:
            payload["at"] = data["at"]
            
        return payload

    def _send_notification(self, data: dict) -> Response:
        url = self._prepare_url()
        params = {"access_token": data["access_token"]}
        payload = self._prepare_data(data)
        
        response = requests.post(
            url,
            params=params,  # access_token作为查询参数
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        return self._create_response(response)
