from datetime import datetime
from enum import Enum
from urllib.parse import urljoin

from pydantic import conint
from pydantic import Field
from pydantic import FilePath
from pydantic import HttpUrl
from pydantic import root_validator
from pydantic import validator

from ..exceptions import ResourceError
from ..models.resource import Provider
from ..models.resource import ProviderResource
from ..models.response import Response
from ..models.schema import ResourceSchema
from ..utils import requests


class PushoverSound(str, Enum):
    pushover = "pushover"
    bike = "bike"
    bugle = "bugle"
    cash_register = "cashregister"
    classical = "classical"
    cosmic = "cosmic"
    falling = "falling"
    gamelan = "gamelan"
    incoming = "incoming"
    intermission = "intermission"
    magic = "magic"
    mechanical = "mechanical"
    piano_bar = "pianobar"
    siren = "siren"
    space_alarm = "spacealarm"
    tug_boat = "tugboat"
    alien = "alien"
    climb = "climb"
    persistent = "persistent"
    echo = "echo"
    updown = "updown"
    none = None


class PushoverBaseSchema(ResourceSchema):
    token: str = Field(..., description="Your application's API token ")


class PushoverSchema(PushoverBaseSchema):
    _values_to_exclude = ("attachment",)
    user: PushoverBaseSchema.one_or_more_of(str) = Field(
        ..., description="The user/group key (not e-mail address) of your user (or you)"
    )
    message: str = Field(..., description="Your message")
    attachment: FilePath = Field(
        None, description="An image attachment to send with the message"
    )
    device: PushoverBaseSchema.one_or_more_of(str) = Field(
        None,
        description="Your user's device name to send the message directly to that device,"
        " rather than all of the user's devices",
    )
    title: str = Field(
        None, description="Your message's title, otherwise your app's name is used"
    )
    url: HttpUrl = Field(
        None, description="A supplementary URL to show with your message"
    )
    url_title: str = Field(
        None,
        description="A title for your supplementary URL, otherwise just the URL is shown",
    )
    priority: conint(ge=1, le=5) = Field(
        None,
        description="send as -2 to generate no notification/alert, -1 to always send as a quiet notification,"
        " 1 to display as high-priority and bypass the user's quiet hours,"
        " or 2 to also require confirmation from the user",
    )
    sound: PushoverSound = Field(
        None,
        description="The name of one of the sounds supported by device clients to override the "
        "user's default sound choice ",
    )
    timestamp: datetime = Field(
        None,
        description="A Unix timestamp of your message's date and time to display to the user,"
        " rather than the time your message is received by our API ",
    )
    html: bool = Field(None, description="Enable HTML formatting")
    monospace: bool = Field(None, description="Enable monospace messages")
    retry: conint(ge=30) = Field(
        None,
        description="Specifies how often (in seconds) the Pushover servers will send the same notification to the user."
        " requires setting priority to 2",
    )
    expire: conint(le=10800) = Field(
        None,
        description="Specifies how many seconds your notification will continue to be retried for "
        "(every retry seconds). requires setting priorty to 2",
    )
    callback: HttpUrl = Field(
        None,
        description="A publicly-accessible URL that our servers will send a request to when the user has"
        " acknowledged your notification. requires setting priorty to 2",
    )
    tags: PushoverBaseSchema.one_or_more_of(str) = Field(
        None,
        description="Arbitrary tags which will be stored with the receipt on our servers",
    )

    @validator("html", "monospace")
    def bool_to_num(cls, v):
        return int(v)

    @validator("user", "device", "tags")
    def to_csv(cls, v):
        return cls.to_comma_separated(v)

    @validator("timestamp")
    def to_timestamp(cls, v: datetime):
        return v.timestamp()

    @root_validator
    def html_or_monospace(cls, values):
        if all(value in values for value in ("html", "monospace")):
            raise ValueError("Cannot use both 'html' and 'monospace'")
        return values


class PushoverMixin:
    name = "pushover"
    base_url = "https://api.pushover.net/1/"
    path_to_errors = ("errors",)


class PushoverSounds(PushoverMixin, ProviderResource):
    resource_name = "sounds"
    sounds_url = "sounds.json"

    schema_model = PushoverBaseSchema

    def _get_resource(self, data: PushoverBaseSchema):
        url = urljoin(self.base_url, self.sounds_url)
        response, errors = requests.get(
            url, params=data.to_dict(), path_to_errors=self.path_to_errors
        )
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return list(response.json()["sounds"].keys())


class PushoverLimits(PushoverMixin, ProviderResource):
    resource_name = "limits"
    limits_url = "apps/limits.json"

    schema_model = PushoverBaseSchema

    def _get_resource(self, data: PushoverBaseSchema):
        url = urljoin(self.base_url, self.limits_url)
        response, errors = requests.get(
            url, params=data.to_dict(), path_to_errors=self.path_to_errors
        )
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return response.json()


class Pushover(PushoverMixin, Provider):
    """Send Pushover notifications"""

    message_url = "messages.json"
    site_url = "https://pushover.net/"
    name = "pushover"

    _resources = {"sounds": PushoverSounds(), "limits": PushoverLimits()}

    schema_model = PushoverSchema

    def _send_notification(self, data: PushoverSchema) -> Response:
        url = urljoin(self.base_url, self.message_url)
        files = []
        if data.attachment:
            files = requests.file_list_for_request(data.attachment, "attachment")
        payload = data.to_dict()
        response, errors = requests.post(
            url, data=payload, files=files, path_to_errors=self.path_to_errors
        )
        return self.create_response(payload, response, errors)

    @property
    def metadata(self) -> dict:
        m = super().metadata
        m["message_url"] = self.message_url
        return m
