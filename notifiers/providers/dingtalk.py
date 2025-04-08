from ..core import Provider, Response
from ..utils import requests


class DingTalk(Provider):
    """Send DingTalk notifications via Robot Webhook"""

    base_url = "https://oapi.dingtalk.com/robot/send"
    site_url = "https://open.dingtalk.com/document/"
    name = "dingtalk"
    path_to_errors = ("errmsg",)

    _required = {
        "required": ["access_token", "msg_data"],
        "oneOf": [{"required": ["msg_data.text"]}, {"required": ["msg_data.markdown"]}, {"required": ["msg_data.link"]}, {"required": ["msg_data.actionCard"]}],
    }

    _schema = {
        "type": "object",
        "properties": {
            "access_token": {"type": "string", "title": "Webhook access token", "description": "Obtain from DingTalk Robot settings", "minLength": 1},
            "msg_data": {
                "type": "object",
                "properties": {
                    "msgtype": {"type": "string", "enum": ["text", "markdown", "link", "actionCard"], "default": "text"},
                    "text": {
                        "type": "object",
                        "properties": {"content": {"type": "string", "title": "Message content", "maxLength": 20000, "minLength": 1}},
                        "required": ["content"],
                        "additionalProperties": False,
                    },
                    "markdown": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "title": "Message title", "maxLength": 100, "minLength": 1},
                            "text": {"type": "string", "title": "Markdown content", "maxLength": 20000, "minLength": 1},
                        },
                        "required": ["title", "text"],
                        "additionalProperties": False,
                    },
                    "link": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "title": "Link title", "maxLength": 100, "minLength": 1},
                            "text": {"type": "string", "title": "Link description", "maxLength": 500, "minLength": 1},
                            "messageUrl": {"type": "string", "title": "Link URL", "format": "uri", "minLength": 1},
                            "picUrl": {"type": "string", "title": "Image URL", "format": "uri", "default": ""},
                        },
                        "required": ["title", "text", "messageUrl"],
                        "additionalProperties": False,
                    },
                    "actionCard": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "title": "Card title", "maxLength": 100, "minLength": 1},
                            "text": {"type": "string", "title": "Card content", "maxLength": 20000, "minLength": 1},
                            "singleTitle": {"type": "string", "title": "Button text", "maxLength": 50, "minLength": 1},
                            "singleURL": {"type": "string", "title": "Button URL", "format": "uri", "minLength": 1},
                            "btnOrientation": {"type": "string", "title": "Button layout", "enum": ["0", "1"], "default": "0"},
                        },
                        "required": ["title", "text", "singleTitle", "singleURL"],
                        "additionalProperties": False,
                    },
                },
                "required": ["msgtype"],
                "additionalProperties": False,
            },
            "at": {
                "type": "object",
                "properties": {
                    "atMobiles": {"type": "array", "title": "Phone numbers to @", "items": {"type": "string", "pattern": "^1[3-9]\\d{9}$"}, "maxItems": 20},
                    "atUserIds": {"type": "array", "title": "User IDs to @", "items": {"type": "string", "minLength": 1}, "maxItems": 20},
                    "isAtAll": {"type": "boolean", "title": "Notify all members", "default": False},
                },
                "additionalProperties": False,
            },
            "sign": {"type": "string", "title": "Secret signature", "description": "Required if secret is set in webhook", "minLength": 1},
            "timestamp": {"type": "string", "title": "Sign timestamp", "pattern": "^\\d{13}$"},
        },
        "additionalProperties": False,
    }

    def _prepare_url(self) -> str:
        """返回基础URL, access_token将通过params传递"""
        return self.base_url

    def _prepare_data(self, data: dict) -> dict:
        """
        构造钉钉机器人要求的消息格式
        文档: https://open.dingtalk.com/document/orgapp-server/custom-robot-access
        """
        payload = {"msgtype": data["msg_data"]["msgtype"], data["msg_data"]["msgtype"]: data["msg_data"][data["msg_data"]["msgtype"]]}

        if "at" in data:
            payload["at"] = data["at"]

        # 安全签名处理
        if "sign" in data and "timestamp" in data:
            payload["sign"] = data["sign"]
            payload["timestamp"] = data["timestamp"]

        return payload

    def _send_notification(self, data: dict) -> Response:
        url = self._prepare_url()
        params = {"access_token": data["access_token"]}
        payload = self._prepare_data(data)

        response = requests.post(url, params=params, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})

        return self._create_response(response)
