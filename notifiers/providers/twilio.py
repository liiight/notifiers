from __future__ import annotations

from pydantic import ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from ..core import Provider, Response
from ..models import E164, SchemaModel, Url
from ..utils import requests
from ..utils.helpers import snake_to_camel_case


class TwilioSchema(SchemaModel):
    # Unknown arguments are passed through to the API
    model_config = ConfigDict(extra="allow")

    message: str | None = Field(None, max_length=1_600, description="The text body of the message. Up to 1,600 characters long.")
    account_sid: str = Field(description="The unique id of the Account that sent this message.")
    auth_token: str = Field(description="The user's auth token")
    to: E164 = Field(description="The recipient of the message, in E.164 format")
    from_: str | None = Field(None, alias="from", description="Twilio phone number or the alphanumeric sender ID used")
    messaging_service_id: str | None = Field(None, description="The unique id of the Messaging Service used with the message")
    media_url: Url | None = Field(None, description="The URL of the media you wish to send out with the message")
    status_callback: Url | None = Field(None, description="A URL where Twilio will POST each time your message status changes")
    application_sid: str | None = Field(
        None,
        description="Twilio will POST MessageSid as well as MessageStatus=sent or MessageStatus=failed to the URL in the MessageStatusCallback property of this Application",
    )
    max_price: float | None = Field(
        None,
        description="The total maximum price up to the fourth decimal (0.0001) in US dollars acceptable for the message to be delivered",
    )
    provide_feedback: bool | None = Field(
        None,
        description="Set this value to true if you are sending messages that have a trackable user action and "
        "you intend to confirm delivery of the message using the Message Feedback API",
    )
    validity_period: int | None = Field(None, ge=1, le=14_400, description="The number of seconds that the message can remain in a Twilio queue")

    @model_validator(mode="after")
    def _check_required(self):
        if not (self.is_set("from_") or self.is_set("messaging_service_id")):
            raise PydanticCustomError("required_argument", "Either 'from' or 'messaging_service_id' are required")
        if not (self.is_set("message") or self.is_set("media_url")):
            raise PydanticCustomError("required_argument", "Either 'message' or 'media_url' are required")
        return self


class Twilio(Provider):
    """Send an SMS via a Twilio number"""

    name = "twilio"
    base_url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
    site_url = "https://www.twilio.com/"
    path_to_errors = ("message",)

    schema_model = TwilioSchema

    def _prepare_data(self, data: dict) -> dict:
        if data.get("message"):
            data["body"] = data.pop("message")
        new_data = {
            "auth_token": data.pop("auth_token"),
            "account_sid": data.pop("account_sid"),
        }
        for key, value in data.items():
            camel_case_key = snake_to_camel_case(key)
            new_data[camel_case_key] = value
        return new_data

    def _send_notification(self, data: dict) -> Response:
        account_sid = data.pop("account_sid")
        url = self.base_url.format(account_sid)
        auth = (account_sid, data.pop("auth_token"))
        response, errors = requests.post(url, data=data, auth=auth, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
