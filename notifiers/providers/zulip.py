from enum import Enum
from typing import Union

from pydantic import constr
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator
from pydantic import validator

from ..models.resource import Provider
from ..models.response import Response
from ..models.schema import ResourceSchema
from ..utils import requests


class MessageType(str, Enum):
    private = "private"
    stream = "stream"


class ZulipSchema(ResourceSchema):
    """Send a stream or a private message"""

    api_key: str = Field(..., description="User API Key")
    url: HttpUrl = Field(None, description="Server URL")
    domain: str = Field(None, description="Subdomain to use with zulipchat.com")
    email: EmailStr = Field(..., description='"User email')
    type: MessageType = Field(
        MessageType.stream,
        description="The type of message to be sent. 'private' for a private message and 'stream' for a stream message",
    )
    message: constr(max_length=10000) = Field(
        ..., description="The content of the message", alias="content"
    )
    to: ResourceSchema.one_or_more_of(Union[EmailStr, str]) = Field(
        ...,
        description="The destination stream, or a CSV/JSON-encoded list containing the usernames "
        "(emails) of the recipients",
    )
    topic: constr(max_length=60) = Field(
        None,
        description="The topic of the message. Only required if type is stream, ignored otherwise",
    )

    @validator("to", whole=True)
    def csv(cls, v):
        return ResourceSchema.to_comma_separated(v)

    _values_to_exclude = (
        "email",
        "api_key",
        "domain",
        "url",
    )

    @root_validator
    def root(cls, values):
        if values["type"] is MessageType.stream and not values.get("topic"):
            raise ValueError("'topic' is required when 'type' is 'stream'")

        if "domain" not in values and "url" not in values:
            raise ValueError("Either 'url' or 'domain' are required")

        base_url = values["url"] or f"https://{values['domain']}.zulipchat.com"
        url = f"{base_url}/api/v1/messages"
        values["server_url"] = url

        return values

    class Config:
        json_encoders = {MessageType: lambda v: v.value}


class Zulip(Provider):
    """Send Zulip notifications"""

    name = "zulip"
    site_url = "https://zulipchat.com/api/"
    path_to_errors = ("msg",)

    schema_model = ZulipSchema

    def _send_notification(self, data: ZulipSchema) -> Response:
        auth = data.email, data.api_key
        payload = data.to_dict()
        response, errors = requests.post(
            data.server_url,
            data=payload,
            auth=auth,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(payload, response, errors)
