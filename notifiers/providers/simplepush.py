from __future__ import annotations

from pydantic import Field

from ..core import Provider, Response
from ..models import SchemaModel
from ..utils import requests


class SimplePushSchema(SchemaModel):
    key: str = Field(description="your user key")
    message: str = Field(description="your message")
    title: str | None = Field(None, description="message title")
    event: str | None = Field(None, description="Event ID")


class SimplePush(Provider):
    """Send SimplePush notifications"""

    base_url = "https://api.simplepush.io/send"
    site_url = "https://simplepush.io/"
    name = "simplepush"

    schema_model = SimplePushSchema

    def _prepare_data(self, data: dict) -> dict:
        data["msg"] = data.pop("message")
        return data

    def _send_notification(self, data: dict) -> Response:
        path_to_errors = ("message",)
        response, errors = requests.post(self.base_url, data=data, path_to_errors=path_to_errors)
        return self.create_response(data, response, errors)
