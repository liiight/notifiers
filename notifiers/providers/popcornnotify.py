from pydantic import Field
from pydantic import validator

from ..models.provider import Provider
from ..models.provider import ResourceSchema
from ..models.response import Response
from ..utils import requests


class PopcornNotifySchema(ResourceSchema):
    message: str = Field(..., description="The message to send")
    api_key: str = Field(..., description="The API key")
    subject: str = Field(
        None,
        description="The subject of the email. It will not be included in text messages",
    )
    recipients: ResourceSchema.one_or_more_of(str) = Field(
        ...,
        description="The recipient email address or phone number.Or an array of email addresses and phone numbers",
    )

    @validator("recipients")
    def recipient_to_comma(cls, v):
        return cls.to_comma_separated(v)


class PopcornNotify(Provider):
    """Send PopcornNotify notifications"""

    base_url = "https://popcornnotify.com/notify"
    site_url = "https://popcornnotify.com/"
    name = "popcornnotify"
    path_to_errors = ("error",)

    schema_model = PopcornNotifySchema

    def _send_notification(self, data: PopcornNotifySchema) -> Response:
        data = data.to_dict()
        response, errors = requests.post(
            url=self.base_url, json=data, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
