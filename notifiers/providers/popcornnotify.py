from __future__ import annotations

from pydantic import ConfigDict, Field

from ..core import Provider, Response
from ..models import Email, OneOrMore, SchemaModel
from ..utils import requests
from ..utils.helpers import list_to_commas


class PopcornNotifySchema(SchemaModel):
    # Unknown arguments are passed through to the API
    model_config = ConfigDict(extra="allow")

    message: str = Field(description="The message to send")
    api_key: str = Field(description="The API key")
    recipients: OneOrMore[Email] = Field(description="The recipient email address or phone number. Or an array of email addresses and phone numbers")
    subject: str | None = Field(None, description="The subject of the email. It will not be included in text messages.")


class PopcornNotify(Provider):
    """Send PopcornNotify notifications"""

    base_url = "https://popcornnotify.com/notify"
    site_url = "https://popcornnotify.com/"
    name = "popcornnotify"
    path_to_errors = ("error",)

    schema_model = PopcornNotifySchema

    def _prepare_data(self, data: dict) -> dict:
        if isinstance(data["recipients"], str):
            data["recipients"] = [data["recipients"]]
        data["recipients"] = list_to_commas(data["recipients"])
        return data

    def _send_notification(self, data: dict) -> Response:
        response, errors = requests.post(url=self.base_url, json=data, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
