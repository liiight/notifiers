from pydantic import Field

from ..models.provider import Provider
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests


class SimplePushSchema(SchemaModel):
    key: str = Field(..., description="Your user key")
    message: str = Field(..., description="Your message", alias="msg")
    title: str = Field(None, description="Message title")
    event: str = Field(None, description="Event Id")


class SimplePush(Provider):
    """Send SimplePush notifications"""

    base_url = "https://api.simplepush.io/send"
    site_url = "https://simplepush.io/"
    name = "simplepush"
    path_to_errors = ("message",)

    schema_model = SimplePushSchema

    def _send_notification(self, data: SimplePushSchema) -> Response:
        data = data.to_dict()
        response, errors = requests.post(
            self.base_url, data=data, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
