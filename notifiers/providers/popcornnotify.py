from ..core import Provider
from ..core import Response
from ..utils import requests
from ..utils.schema.helpers import list_to_commas
from ..utils.schema.helpers import one_or_more


class PopcornNotify(Provider):
    """Send PopcornNotify notifications"""

    base_url = "https://popcornnotify.com/notify"
    site_url = "https://popcornnotify.com/"
    name = "popcornnotify"
    path_to_errors = ("error",)

    _required = {"required": ["message", "api_key", "recipients"]}

    _schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "title": "The message to send"},
            "api_key": {"type": "string", "title": "The API key"},
            "recipients": one_or_more(
                {
                    "type": "string",
                    "format": "email",
                    "title": "The recipient email address or phone number."
                    " Or an array of email addresses and phone numbers",
                }
            ),
            "subject": {
                "type": "string",
                "title": "The subject of the email. It will not be included in text messages.",
            },
        },
    }

    def _prepare_data(self, data: dict) -> dict:
        if isinstance(data["recipients"], str):
            data["recipients"] = [data["recipients"]]
        data["recipients"] = list_to_commas(data["recipients"])
        return data

    def _send_notification(self, data: dict) -> Response:
        response, errors = requests.post(
            url=self.base_url, json=data, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
