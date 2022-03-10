from ..core import Provider
from ..core import Response
from ..utils import requests


class DingTalk(Provider):
    """Send DingTalk notifications"""

    base_url = "https://oapi.dingtalk.com/robot/send?access_token={}"
    site_url = "https://oapi.dingtalk.com/"
    path_to_errors = ("message",)
    name = "dingtalk"

    _required = {"required": ["access_token", "msg_data"]}
    _schema = {
        "type": "object",
        "properties": {
            "access_token": {
                "type": "string",
                "title": "access token to pair a channel to receive notification",
            },
            "msg_data": {
                "type": "object",
                "title": "dingtalk message body definition",
                "properties": {
                    "msgtype": {
                        "type": "string",
                        "title": "choose a message type, these type supported: text, markdown, link, actionCard"
                    },
                    "text": {
                        "type": "object",
                        "title": "text message",
                        "properties": {
                            "content": {
                                "type": "string",
                                "title": "text message content"
                            }
                        },
                        "required": ["content"]
                    },
                    "markdown": {
                        "type": "object",
                        "title": "markdown message",
                        "properties": {
                            "title": {
                                "type": "string",
                                "title": "message title"
                            },
                            "text": {
                                "type": "string",
                                "title": "markdown message content"
                            }
                        },
                        "required": ["title", "text"]
                    },
                    "link": {
                        "type": "object",
                        "title": "link message",
                        "properties": {
                            "title": {
                                "type": "string",
                                "title": "message title"
                            },
                            "text": {
                                "type": "string",
                                "title": "message content"
                            },
                            "messageUrl": {
                                "type": "string",
                                "title": "link url"
                            }
                        },
                        "required": ["title", "text", "messageUrl"]
                    },
                    "actionCard": {
                        "type": "object",
                        "title": "card message",
                        "properties": {
                            "title": {
                                "type": "string",
                                "title": "message title"
                            },
                            "text": {
                                "type": "string",
                                "title": "message content"
                            },
                            "singleTitle": {
                                "type": "string",
                                "title": "title for card footage button, like 'Read more.' button"
                            },
                            "singleURL": {
                                "type": "string",
                                "title": "link url when user click card button"
                            }
                        },
                        "required": ["title", "text", "singleTitle", "singleURL"]
                    },
                },
                "required": ["msgtype"]
            },
        },
        "additionalProperties": False,
    }

    def _send_notification(self, data: dict) -> Response:
        access_token = data.pop("access_token")
        url = self.base_url.format(access_token)
        response, errors = requests.post(
            url, json=data.pop("msg_data"), path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
