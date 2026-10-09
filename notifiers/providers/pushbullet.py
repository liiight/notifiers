from __future__ import annotations

from typing import Literal

from pydantic import Field

from ..core import Provider, ProviderResource, Response
from ..exceptions import ResourceError
from ..models import Email, SchemaModel
from ..utils import requests


class PushbulletDevicesSchema(SchemaModel):
    token: str = Field(description="API access token")


class PushbulletSchema(SchemaModel):
    message: str = Field(description="Body of the push")
    token: str = Field(description="API access token")
    title: str | None = Field(None, description="Title of the push")
    type_: Literal["note", "link"] = Field(
        "note",
        description='Type of the push, one of "note" or "link"',
        alias="type",
    )
    url: str | None = Field(None, description='URL field, used for type="link" pushes')
    source_device_iden: str | None = Field(None, description="Device iden of the sending device")
    device_iden: str | None = Field(None, description="Device iden of the target device, if sending to a single device")
    client_iden: str | None = Field(
        None,
        description="Client iden of the target client, sends a push to all users who have granted access to this client. The current user must own this client",
    )
    channel_tag: str | None = Field(
        None,
        description="Channel tag of the target channel, sends a push to all people who are subscribed to this channel. The current user must own this channel.",
    )
    email: Email | None = Field(
        None,
        description="Email address to send the push to. If there is a pushbullet user with this address, they get a push, otherwise they get an email",
    )
    guid: str | None = Field(
        None,
        description="Unique identifier set by the client, used to identify a push in case you receive it "
        "from /v2/everything before the call to /v2/pushes has completed. This should be a unique"
        " value. Pushes with guid set are mostly idempotent, meaning that sending another push "
        "with the same guid is unlikely to create another push (it will return the previously"
        " created push).",
    )


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

    schema_model = PushbulletDevicesSchema

    def _get_resource(self, data: dict) -> list:
        headers = self._get_headers(data["token"])
        response, errors = requests.get(self.devices_url, headers=headers, path_to_errors=self.path_to_errors)
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

    _resources = {"devices": PushbulletDevices()}

    schema_model = PushbulletSchema

    def _prepare_data(self, data: dict) -> dict:
        data["body"] = data.pop("message")
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
