from ..core import Provider
from ..core import Response
from ..utils import requests


class SimplePush(Provider):
    """Send SimplePush notifications"""

    base_url = "https://api.simplepush.io/send"
    site_url = "https://simplepush.io/"
    name = "simplepush"

    _required = {"required": ["key", "message"]}
    _schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "title": "your user key"},
            "message": {"type": "string", "title": "your message"},
            "title": {"type": "string", "title": "message title"},
            "event": {"type": "string", "title": "Event ID"},
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        data["msg"] = data.pop("message")
        return data

    def _send_notification(self, data: dict) -> Response:
        path_to_errors = ("message",)
        response, errors = requests.post(
            self.base_url, data=data, path_to_errors=path_to_errors
        )
        return self.create_response(data, response, errors)
