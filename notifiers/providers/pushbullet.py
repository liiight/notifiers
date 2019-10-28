from ..core import Provider
from ..core import ProviderResource
from ..core import Response
from ..exceptions import ResourceError
from ..utils import requests


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
