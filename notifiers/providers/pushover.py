from __future__ import annotations

from pydantic import ConfigDict, Field

from ..core import Provider, ProviderResource, Response
from ..exceptions import ResourceError
from ..models import FilePath, OneOrMore, SchemaModel, Timestamp, Url
from ..utils import requests
from ..utils.helpers import list_to_commas


class PushoverResourceSchema(SchemaModel):
    # Unknown arguments are passed through to the API
    model_config = ConfigDict(extra="allow")

    token: str = Field(description="your application's API token")


class PushoverSchema(SchemaModel):
    user: OneOrMore[str] = Field(description="the user/group key (not e-mail address) of your user (or you)")
    message: str = Field(description="your message")
    title: str | None = Field(None, description="your message's title, otherwise your app's name is used")
    token: str = Field(description="your application's API token")
    device: OneOrMore[str] | None = Field(None, description="your user's device name to send the message directly to that device")
    priority: int | None = Field(None, ge=-2, le=2, description="notification priority")
    url: Url | None = Field(None, description="a supplementary URL to show with your message")
    url_title: str | None = Field(None, description="a title for your supplementary URL, otherwise just the URL is shown")
    sound: str | None = Field(
        None,
        description="the name of one of the sounds supported by device clients to override the user's default sound choice. See `sounds` resource",
    )
    timestamp: Timestamp | None = Field(
        None,
        description="a Unix timestamp of your message's date and time to display to the user, rather than the time your message is received by our API",
    )
    retry: int | None = Field(
        None,
        ge=30,
        description="how often (in seconds) the Pushover servers will send the same notification to the user. priority must be set to 2",
    )
    expire: int | None = Field(
        None,
        le=86400,
        description="how many seconds your notification will continue to be retried for. priority must be set to 2",
    )
    callback: Url | None = Field(
        None,
        description="a publicly-accessible URL that our servers will send a request to when the user has acknowledged your notification. priority must be set to 2",
    )
    html: bool | None = Field(None, description="enable HTML formatting")
    attachment: FilePath | None = Field(None, description="an image attachment to send with the message")


class PushoverMixin:
    name = "pushover"
    base_url = "https://api.pushover.net/1/"
    path_to_errors = ("errors",)


class PushoverResourceMixin(PushoverMixin):
    schema_model = PushoverResourceSchema


class PushoverSounds(PushoverResourceMixin, ProviderResource):
    resource_name = "sounds"
    sounds_url = "sounds.json"

    def _get_resource(self, data: dict):
        url = self.base_url + self.sounds_url
        params = {"token": data["token"]}
        response, errors = requests.get(url, params=params, path_to_errors=self.path_to_errors)
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return list(response.json()["sounds"].keys())


class PushoverLimits(PushoverResourceMixin, ProviderResource):
    resource_name = "limits"
    limits_url = "apps/limits.json"

    def _get_resource(self, data: dict):
        url = self.base_url + self.limits_url
        params = {"token": data["token"]}
        response, errors = requests.get(url, params=params, path_to_errors=self.path_to_errors)
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

    def _prepare_data(self, data: dict) -> dict:
        data["user"] = list_to_commas(data["user"])
        if data.get("device"):
            data["device"] = list_to_commas(data["device"])
        if data.get("html") is not None:
            data["html"] = int(data["html"])
        if data.get("attachment") and not isinstance(data["attachment"], list):
            data["attachment"] = [data["attachment"]]
        return data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url + self.message_url
        headers = {}
        files = []
        if data.get("attachment"):
            files = requests.file_list_for_request(data["attachment"], "attachment")
        response, errors = requests.post(
            url,
            data=data,
            headers=headers,
            files=files,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(data, response, errors)

    @property
    def metadata(self) -> dict:
        m = super().metadata
        m["message_url"] = self.message_url
        return m
