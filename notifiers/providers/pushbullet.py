from enum import Enum

from pydantic import EmailStr
from pydantic import Field
from pydantic import FilePath
from pydantic import HttpUrl
from pydantic import root_validator

from ..exceptions import ResourceError
from ..models.provider import Provider
from ..models.provider import ProviderResource
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests


class PushbulletType(Enum):
    note = "note"
    file = "file"
    link = "link"


class PushbulletSchema(SchemaModel):
    type: PushbulletType = Field(PushbulletType.note, description="Type of the push")
    body: str = Field(
        ...,
        description="Body of the push, used for all types of pushes",
        alias="message",
    )
    token: str = Field(..., description="API access token")
    title: str = Field(
        None, description="Title of the push, used for all types of pushes"
    )
    url: HttpUrl = Field(None, description='URL field, used for type="link" pushes')
    file: FilePath = Field(None, description="A path to a file to upload")
    source_device_iden: str = Field(
        None,
        description='Device iden of the sending device. Optional. Example: "ujpah72o0sjAoRtnM0jc"',
    )
    device_iden: str = Field(
        None,
        description="Device iden of the target device, if sending to a single device. "
        'Appears as target_device_iden on the push. Example: "ujpah72o0sjAoRtnM0jc"',
    )
    client_iden: str = Field(
        None,
        description="Client iden of the target client, sends a push to all users who have granted access"
        ' to this client. The current user must own this client. Example: "ujpah72o0sjAoRtnM0jc"',
    )
    channel_tag: str = Field(
        None,
        description="Channel tag of the target channel, sends a push to all people who are subscribed to this channel. "
        "The current user must own this channel.",
    )
    email: EmailStr = Field(
        None,
        description="Email address to send the push to. If there is a pushbullet user with this address, "
        'they get a push, otherwise they get an email. Example: "elon@teslamotors.com"',
    )
    guid: str = Field(
        None,
        description="Unique identifier set by the client, used to identify a push in case you receive it from "
        "/v2/everything before the call to /v2/pushes has completed. This should be a unique value."
        " Pushes with guid set are mostly idempotent, meaning that sending another push with the same"
        " guid is unlikely to create another push (it will return the previously created push). "
        'Example: "993aaa48567d91068e96c75a74644159"',
    )

    @root_validator(pre=True)
    def validate_types(cls, values):
        type = values["type"]
        if type is PushbulletType.link and not values.get("url"):
            raise ValueError("'url' must be passed when push type is link")
        elif type is PushbulletType.file and not values.get("file"):
            raise ValueError("'file' must be passed when push type is file")
        return values


class PushbulletMixin:
    """Shared attributes between :class:`PushbulletDevices` and :class:`Pushbullet`"""

    name = "pushbullet"
    path_to_errors = "error", "message"

    def _get_headers(self, token: str) -> dict:
        return {"Access-Token": token}


class PushbulletDevices(PushbulletMixin, ProviderResource):
    """Return a list of Pushbullet devices associated to a token"""

    resource_name = "devices"
    devices_url = "https://api.pushbullet.com/v2/devices"

    _required = {"required": ["token"]}
    _schema = {
        "type": "object",
        "properties": {"token": {"type": "string", "title": "API access token"}},
        "additionalProperties": False,
    }

    def _get_resource(self, data: dict) -> list:
        headers = self._get_headers(data["token"])
        response, errors = requests.get(
            self.devices_url, headers=headers, path_to_errors=self.path_to_errors
        )
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return response.json()["devices"]


class Pushbullet(PushbulletMixin, Provider):
    """Send Pushbullet notifications"""

    base_url = "https://api.pushbullet.com/v2/pushes"
    site_url = "https://www.pushbullet.com"

    __type = {
        "type": "string",
        "title": 'Type of the push, one of "note" or "link"',
        "enum": ["note", "link"],
    }

    _resources = {"devices": PushbulletDevices()}
    _required = {"required": ["message", "token"]}
    _schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "title": "Body of the push"},
            "token": {"type": "string", "title": "API access token"},
            "title": {"type": "string", "title": "Title of the push"},
            "type": __type,
            "type_": __type,
            "url": {
                "type": "string",
                "title": 'URL field, used for type="link" pushes',
            },
            "source_device_iden": {
                "type": "string",
                "title": "Device iden of the sending device",
            },
            "device_iden": {
                "type": "string",
                "title": "Device iden of the target device, if sending to a single device",
            },
            "client_iden": {
                "type": "string",
                "title": "Client iden of the target client, sends a push to all users who have granted access to "
                "this client. The current user must own this client",
            },
            "channel_tag": {
                "type": "string",
                "title": "Channel tag of the target channel, sends a push to all people who are subscribed to "
                "this channel. The current user must own this channel.",
            },
            "email": {
                "type": "string",
                "format": "email",
                "title": "Email address to send the push to. If there is a pushbullet user with this address,"
                " they get a push, otherwise they get an email",
            },
            "guid": {
                "type": "string",
                "title": "Unique identifier set by the client, used to identify a push in case you receive it "
                "from /v2/everything before the call to /v2/pushes has completed. This should be a unique"
                " value. Pushes with guid set are mostly idempotent, meaning that sending another push "
                "with the same guid is unlikely to create another push (it will return the previously"
                " created push).",
            },
        },
        "additionalProperties": False,
    }

    @property
    def defaults(self) -> dict:
        return {"type": "note"}

    def _prepare_data(self, data: dict) -> dict:
        data["body"] = data.pop("message")

        # Workaround since `type` is a reserved word
        if data.get("type_"):
            data["type"] = data.pop("type_")
        return data

    def _send_notification(self, data: dict) -> Response:
        headers = self._get_headers(data.pop("token"))
        response, errors = requests.post(
            self.base_url,
            json=data,
            headers=headers,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(data, response, errors)
