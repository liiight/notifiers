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
        "type": "object",
        "properties": {
            "access_token": {
                "type": "string",
                "title": "Webhook access token",
                "description": "Obtain from DingTalk Robot settings"
            },
            "msg_data": {
                "type": "object",
                "properties": {
                    "msgtype": {
                        "type": "string",
                        "enum": ["text", "markdown", "link", "actionCard"],
                        "default": "text"
                    },
                    "text": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "maxLength": 20000
                            }
                        },
                        "required": ["content"]
                    },
                    "markdown": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "maxLength": 100
                            },
                            "text": {
                                "type": "string",
                                "maxLength": 20000
                            }
                        },
                        "required": ["title", "text"]
                    },
                    "link": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "maxLength": 100
                            },
                            "text": {
                                "type": "string",
                                "maxLength": 500
                            },
                            "messageUrl": {
                                "type": "string",
                                "format": "uri"
                            },
                            "picUrl": {
                                "type": "string",
                                "format": "uri",
                                "default": ""
                            }
                        },
                        "required": ["title", "text", "messageUrl"]
                    },
                    "actionCard": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "maxLength": 100
                            },
                            "text": {
                                "type": "string",
                                "maxLength": 20000
                            },
                            "singleTitle": {
                                "type": "string",
                                "maxLength": 50
                            },
                            "singleURL": {
                                "type": "string",
                                "format": "uri"
                            },
                            "btnOrientation": {
                                "type": "string",
                                "enum": ["0", "1"],
                                "default": "0"
                            }
                        },
                        "required": ["title", "text", "singleTitle", "singleURL"]
                    }
                },
                "required": ["msgtype"],
                "additionalProperties": False
            },
            "at": {
                "type": "object",
                "properties": {
                    "atMobiles": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": "^1[3-9]\\d{9}$"
                        }
                    },
                    "atUserIds": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1
                        }
                    },
                    "isAtAll": {
                        "type": "boolean",
                        "default": False
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    def _prepare_url(self, access_token: str) -> str:
        return f"{self.base_url}?access_token={access_token}"

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
        url = self._prepare_url(data["access_token"])
        payload = self._prepare_data(data)
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        return self._create_response(response)
