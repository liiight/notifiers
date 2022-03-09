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
            },
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        return data

    def _send_notification(self, data: dict) -> Response:
        access_token = data.pop("access_token")
        url = self.base_url.format(access_token)
        response, errors = requests.post(
            url, json=data.pop('msg_data'), path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
