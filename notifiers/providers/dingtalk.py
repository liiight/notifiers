from ..core import Provider
from ..core import Response
from ..utils import requests


class DingTalk(Provider):
    """Send DingTalk notifications"""

    base_url = "https://oapi.dingtalk.com/robot/send?access_token={}"
    site_url = "https://oapi.dingtalk.com/"
    path_to_errors = ("message",)
    name = "dingtalk"

    _required = {"required": ["access_token", "message"]}
    _schema = {
        "type": "object",
        "properties": {
            "access_token": {
                "type": "string",
                "title": "access token to pair a channel to receive notification",
            },
            "msg_type": {
                "type": "string",
                "title": "choose a message type, these type are supported: text, markdown, link, action_card",
                "enum": ["text", "markdown", "link", "action_card"]
            },
            "message": {
                "type": "string",
                "title": "This is the text that will be posted to the dingtalk",
                "maxLength": 4096,
            },
            "msg_title": {
                "type": "string",
                "title": "title for markdown message and card message"
            },
            "msg_url": {
                "type": "string",
                "format": "uri",
                "title": "url for markdown message"
            },
            "msg_btn_title": {
                "type": "string",
                "title": "title for card message button, like 'Read more.'"
            },
            "msg_btn_url": {
                "type": "string",
                "format": "uri",
                "title": "url for card message button"
            }
        },
        "additionalProperties": False,
    }

    @property
    def defaults(self) -> dict:
        return {"msg_type": "text"}

    def _prepare_data(self, data: dict) -> dict:
        text = data.pop("message")
        mapping_key = {
            "msg_title": "title",
            "msg_url": "messageUrl",
            "msg_btn_title": "singleTitle",
            "msg_btn_url": "singleURL"
        }

        new_data = {
            "access_token": data.pop("access_token"),
            "msgtype": data.pop("msg_type")
        }

        if new_data["msgtype"] != "text":
            camel_case_str = "".join(word.capitalize() for word in new_data["msgtype"].split("_"))
            new_data["msgtype"] = camel_case_str[0].lower() + camel_case_str[1:]

            new_data[new_data["msgtype"]] = {"text": text}
            for key in data:
                new_data[new_data["msgtype"]][mapping_key[key]] = data[key]
        else:
            new_data["text"] = {"content": text}

        return new_data

    def _send_notification(self, data: dict) -> Response:
        access_token = data.pop("access_token")
        url = self.base_url.format(access_token)
        response, errors = requests.post(
            url, json=data, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
