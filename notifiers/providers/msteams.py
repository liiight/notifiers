from ..core import Provider
from ..core import Response
from ..utils import requests


class MSTeams(Provider):
    """Send MS Teams notification with title and message."""

    base_url = "https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook"
    site_url = "https://www.microsoft.com/en-en/microsoft-teams"
    name = "msteams"

    _schema = {
        "type": "object",
        "properties": {
            "webhook_url": {
                "type": "string",
                "title": "webhook url for MS Teams channel",
            },
            "message": {"type": "string", "title": "body of the notification"},
            "title": {"type": "string", "title": "title of notification"},
        },
        "additionalProperties": True
    }

    _required = {"required": ["message", "webhook_url"]}

    def _prepare_data(self, data: dict) -> dict:
        text = data.pop("message")
        data["text"] = text
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("webhook_url")
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
