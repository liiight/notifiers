from enum import Enum
from typing import Union
from urllib.parse import urljoin

from pydantic import constr
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator
from pydantic import ValidationError
from pydantic import validator

from ..models.provider import Provider
from ..models.provider import ResourceSchema
from ..models.response import Response
from ..utils import requests


class ZulipUrl(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            url = HttpUrl(v)
        except ValidationError:
            url = f"https://{v}.zulipchat.com"
        return urljoin(url, "/api/v1/messages")


class MessageType(Enum):
    private = "private"
    stream = "stream"


class ZulipSchema(ResourceSchema):
    """Send a stream or a private message"""

    api_key: str = Field(..., description="User API Key")
    url_or_domain: ZulipUrl = Field(
        ...,
        description="Either a full server URL or subdomain to be used with zulipchat.com",
    )
    email: EmailStr = Field(..., description='"User email')
    type: MessageType = Field(
        MessageType.stream,
        description="The type of message to be sent. private for a private message and stream for a stream message",
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

    _values_to_exclude = "email", "api_key", "url_or_domain"

    @root_validator
    def root(cls, values):
        if values["type"] is MessageType.stream and not values.get("topic"):
            raise ValueError("'topic' is required when 'type' is 'stream'")

        return values

    class Config:
        json_encoders = {MessageType: lambda v: v.value}


class Zulip(Provider):
    """Send Zulip notifications"""

    name = "zulip"
    site_url = "https://zulipchat.com/api/"
    path_to_errors = ("msg",)

    def _send_notification(self, data: ZulipSchema) -> Response:
        auth = data.email, data.api_key
        payload = data.to_dict()
        response, errors = requests.post(
            data.url_or_domain,
            data=payload,
            auth=auth,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(payload, response, errors)
