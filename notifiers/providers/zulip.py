from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from ..core import Provider, Response
from ..exceptions import NotifierException
from ..models import Email, SchemaModel, Url
from ..utils import requests


class ZulipSchema(SchemaModel):
    message: str = Field(description="Message content")
    email: Email = Field(description="User email")
    api_key: str = Field(description="User API Key")
    type_: Literal["stream", "private"] = Field(
        "stream",
        description="Type of message to send",
        alias="type",
    )
    to: str = Field(description="Target of the message")
    subject: str | None = Field(None, description="Title of the stream message. Required when using stream.")
    domain: str | None = Field(None, min_length=1, description="Zulip cloud domain")
    server: Url | None = Field(None, description="Zulip server URL. Example: https://myzulip.server.com")

    @model_validator(mode="after")
    def _domain_or_server(self):
        passed = [name for name in ("domain", "server") if self.is_set(name)]
        if not passed:
            raise PydanticCustomError("required_argument", "One of 'domain', 'server' is required")
        if len(passed) > 1:
            raise PydanticCustomError("domain_or_server", "Only one of 'domain' or 'server' is allowed")
        return self


class Zulip(Provider):
    """Send Zulip notifications"""

    name = "zulip"
    site_url = "https://zulipchat.com/api/"
    api_endpoint = "/api/v1/messages"
    base_url = "https://{domain}.zulipchat.com"
    path_to_errors = ("msg",)

    schema_model = ZulipSchema

    def _prepare_data(self, data: dict) -> dict:
        base_url = self.base_url.format(domain=data.pop("domain")) if data.get("domain") else data.pop("server")
        data["url"] = base_url + self.api_endpoint
        data["content"] = data.pop("message")
        return data

    def _validate_data_dependencies(self, data: dict) -> dict:
        if data["type"] == "stream" and not data.get("subject"):
            raise NotifierException(
                provider=self.name,
                message="'subject' is required when 'type' is 'stream'",
                data=data,
            )
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("url")
        auth = (data.pop("email"), data.pop("api_key"))
        response, errors = requests.post(url, data=data, auth=auth, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
