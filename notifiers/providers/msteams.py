from ..core import Provider
from ..core import Response
from ..utils import requests


class MSTeams(Provider):
    """Send MS Teams notification with title and message."""

    base_url = ""
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
            "color": {"type": "string", "title": "color of the card",
                      "pattern": "^#?([A-Fa-f0-9]{6})$"},
            "button": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "title": "Name of the button"},
                    "target": {"type": "string", "title": "URL address of the target",
                               "pattern": "^https?://"},
                }
            }
        },
        "additionalProperties": True,
    }

    _required = {"required": ["message", "webhook_url"]}

    def _prepare_data(self, data: dict) -> dict:
        # process text/message
        text = data.pop("message")
        data["text"] = text

        # process color
        if "color" in data.keys():
            clr = data.pop("color")
            data["themeColor"] = f"#{clr}" if not clr.startswith("#") else clr

        # process button
        if "button" in data.keys():
            if "potentialAction" not in data.keys():
                data["potentialAction"] = []
            button = {
                "@context": "http://schema.org",
                "@type": "ViewAction",
                "name": data["button"]["name"],
                "target": [data["button"]["target"]],
            }
            data["potentialAction"].append(button)
            data.pop("button")
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("webhook_url")
        print(data)
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
