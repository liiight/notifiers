import re
from typing import List
from typing import Union

from pydantic import condecimal
from pydantic import conint
from pydantic import constr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator

from ..models.provider import Provider
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests
from ..utils.helpers import snake_to_camel_case

E164_re = re.compile(r"^\+?[1-9]\d{1,14}$")


class E164(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not E164_re.match(v):
            raise ValueError("Value is not an E.164 formatted number")
        return cls(v)


class TwilioSchema(SchemaModel):
    """To send a new outgoing message, make an HTTP POST to this Messages list resource URI"""

    account_sid: str = Field(
        ..., description="The SID of the Account that will create the resource"
    )
    auth_token: str = Field(..., description="user authentication token")
    to: Union[E164, str] = Field(
        ...,
        description="The destination phone number in E.164 format for SMS/MMS or Channel user address for other"
        " 3rd-party channels",
    )
    status_callback: HttpUrl = Field(
        None,
        description="The URL we should call using the status_callback_method to send status information to your "
        "application. If specified, we POST these message status changes to the URL: queued, failed,"
        " sent, delivered, or undelivered. Twilio will POST its standard request parameters as well as "
        "some additional parameters including MessageSid, MessageStatus, and ErrorCode. "
        "If you include this parameter with the messaging_service_sid, we use this URL instead of the "
        "Status Callback URL of the Messaging Service",
    )
    application_sid: str = Field(
        None,
        description="The SID of the application that should receive message status. We POST a message_sid parameter "
        "and a message_status parameter with a value of sent or failed to the application's "
        "message_status_callback. If a status_callback parameter is also passed, "
        "it will be ignored and the application's message_status_callback parameter will be used",
    )
    max_price: condecimal(decimal_places=4) = Field(
        None,
        description="The maximum total price in US dollars that you will pay for the message to be delivered. "
        "Can be a decimal value that has up to 4 decimal places. All messages are queued for delivery and "
        "the message cost is checked before the message is sent. If the cost exceeds max_price, "
        "the message will fail and a status of Failed is sent to the status callback. "
        "If max_price is not set, the message cost is not checked",
    )
    provide_feedback: bool = Field(
        None,
        description="Whether to confirm delivery of the message. "
        "Set this value to true if you are sending messages that have a trackable user action and you "
        "intend to confirm delivery of the message using the Message Feedback API",
    )
    validity_period: conint(ge=1, le=14400) = Field(
        None,
        description="How long in seconds the message can remain in our outgoing message queue. "
        "After this period elapses, the message fails and we call your status callback. "
        "Can be between 1 and the default value of 14,400 seconds. After a message has been accepted by a "
        "carrier, however, we cannot guarantee that the message will not be queued after this period. "
        "We recommend that this value be at least 5 seconds",
    )
    smart_encoded: bool = Field(
        None,
        description="Whether to detect Unicode characters that have a similar GSM-7 character and replace them",
    )
    persistent_action: List[str] = Field(
        None, description="Rich actions for Channels Messages"
    )
    from_: E164 = Field(
        None,
        description="A Twilio phone number in E.164 format, an alphanumeric sender ID, or a Channel Endpoint address "
        "that is enabled for the type of message you want to send. Phone numbers or short codes purchased "
        "from Twilio also work here. You cannot, for example, spoof messages from a private cell phone "
        "number. If you are using messaging_service_sid, this parameter must be empty",
    )
    messaging_service_sid: str = Field(
        None,
        description="The SID of the Messaging Service you want to associate with the Message. "
        "Set this parameter to use the Messaging Service Settings and Copilot Features you have "
        "configured and leave the from parameter empty. When only this parameter is set, "
        "Twilio will use your enabled Copilot Features to select the from phone number for delivery",
    )
    message: constr(min_length=1, max_length=1600) = Field(
        None, description="The text of the message you want to send", alias="body"
    )
    media_url: SchemaModel.one_or_more_of(HttpUrl) = Field(
        None,
        description="The URL of the media to send with the message. The media can be of type gif, png, and jpeg and "
        "will be formatted correctly on the recipient's device. The media size limit is 5MB for "
        "supported file types (JPEG, PNG, GIF) and 500KB for other types of accepted media. "
        "You can send images in an SMS message in only the US and Canada",
        max_items=10,
    )

    @root_validator
    def check_values(cls, values):
        if not any(value in values for value in ("message", "media_url")):
            raise ValueError("Either 'message' or 'media_url' are required")

        from_fields = [values.get(v) for v in ("from_", "messaging_service_sid")]
        if not any(from_fields) or all(from_fields):
            raise ValueError(
                "Only one of 'from_' or 'messaging_service_sid' are allowed"
            )

        return values


class Twilio(Provider):
    """Send an SMS via a Twilio number"""

    name = "twilio"
    base_url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
    site_url = "https://www.twilio.com/"
    path_to_errors = ("message",)

    _required = {
        "allOf": [
            {
                "anyOf": [
                    {"anyOf": [{"required": ["from"]}, {"required": ["from_"]}]},
                    {"required": ["messaging_service_id"]},
                ],
                "error_anyOf": "Either 'from' or 'messaging_service_id' are required",
            },
            {
                "anyOf": [{"required": ["message"]}, {"required": ["media_url"]}],
                "error_anyOf": "Either 'message' or 'media_url' are required",
            },
            {"required": ["to", "account_sid", "auth_token"]},
        ]
    }

    _schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "title": "The text body of the message. Up to 1,600 characters long.",
                "maxLength": 1_600,
            },
            "account_sid": {
                "type": "string",
                "title": "The unique id of the Account that sent this message.",
            },
            "auth_token": {"type": "string", "title": "The user's auth token"},
            "to": {
                "type": "string",
                "format": "e164",
                "title": "The recipient of the message, in E.164 format",
            },
            "from": {
                "type": "string",
                "title": "Twilio phone number or the alphanumeric sender ID used",
            },
            "from_": {
                "type": "string",
                "title": "Twilio phone number or the alphanumeric sender ID used",
                "duplicate": True,
            },
            "messaging_service_id": {
                "type": "string",
                "title": "The unique id of the Messaging Service used with the message",
            },
            "media_url": {
                "type": "string",
                "format": "uri",
                "title": "The URL of the media you wish to send out with the message",
            },
            "status_callback": {
                "type": "string",
                "format": "uri",
                "title": "A URL where Twilio will POST each time your message status changes",
            },
            "application_sid": {
                "type": "string",
                "title": "Twilio will POST MessageSid as well as MessageStatus=sent or MessageStatus=failed to the URL "
                "in the MessageStatusCallback property of this Application",
            },
            "max_price": {
                "type": "number",
                "title": "The total maximum price up to the fourth decimal (0.0001) in US dollars acceptable for "
                "the message to be delivered",
            },
            "provide_feedback": {
                "type": "boolean",
                "title": "Set this value to true if you are sending messages that have a trackable user action and "
                "you intend to confirm delivery of the message using the Message Feedback API",
            },
            "validity_period": {
                "type": "integer",
                "title": "The number of seconds that the message can remain in a Twilio queue",
                "minimum": 1,
                "maximum": 14_400,
            },
        },
    }

    def _prepare_data(self, data: dict) -> dict:
        if data.get("message"):
            data["body"] = data.pop("message")
        new_data = {
            "auth_token": data.pop("auth_token"),
            "account_sid": data.pop("account_sid"),
        }
        for key in data:
            camel_case_key = snake_to_camel_case(key)
            new_data[camel_case_key] = data[key]
        return new_data

    def _send_notification(self, data: dict) -> Response:
        account_sid = data.pop("account_sid")
        url = self.base_url.format(account_sid)
        auth = (account_sid, data.pop("auth_token"))
        response, errors = requests.post(
            url, data=data, auth=auth, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
