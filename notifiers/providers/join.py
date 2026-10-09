from __future__ import annotations

import json

import requests
from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from ..core import Provider, ProviderResource, Response
from ..exceptions import ResourceError
from ..models import OneOrMore, SchemaModel, Url
from ..utils.helpers import list_to_commas


class JoinDevicesSchema(SchemaModel):
    api_key: str = Field(alias="apikey", description="user API key")


class JoinSchema(SchemaModel):
    api_key: str = Field(alias="apikey", description="user API key")
    message: str = Field(
        description="usually used as a Tasker or EventGhost command. Can also be used with URLs and Files to add a description for those elements",
    )
    device_id: str = Field("group.all", alias="deviceId", description="The device ID or group ID of the device you want to send the message to")
    device_ids: OneOrMore[str] | None = Field(None, alias="deviceIds", description="A comma separated list of device IDs you want to send the push to")
    device_names: OneOrMore[str] | None = Field(None, alias="deviceNames", description="A comma separated list of device names you want to send the push to")
    url: Url | None = Field(
        None,
        description=" A URL you want to open on the device. If a notification is created with this push, this will make clicking the notification open this URL",
    )
    clipboard: str | None = Field(None, description="some text you want to set on the receiving device’s clipboard")  # noqa: RUF001
    file: Url | None = Field(None, description="a publicly accessible URL of a file")
    sms_number: str | None = Field(None, alias="smsnumber", description="phone number to send an SMS to")
    sms_text: str | None = Field(None, alias="smstext", description="some text to send in an SMS")
    call_number: str | None = Field(None, alias="callnumber", description="number to call to")
    interruption_filter: int | None = Field(None, ge=1, le=4, alias="interruptionFilter", description="set interruption filter mode")
    mms_file: Url | None = Field(None, alias="mmsfile", description="publicly accessible mms file url")
    media_volume: int | None = Field(None, alias="mediaVolume", description="set device media volume")
    ring_volume: str | None = Field(None, alias="ringVolume", description="set device ring volume")
    alarm_volume: str | None = Field(None, alias="alarmVolume", description="set device alarm volume")
    wallpaper: Url | None = Field(None, description="a publicly accessible URL of an image file")
    find: bool | None = Field(None, description="set to true to make your device ring loudly")
    title: str | None = Field(
        None,
        description="If used, will always create a notification on the receiving device with this as the title and text as the notification’s text",  # noqa: RUF001
    )
    icon: Url | None = Field(None, description="notification's icon URL")
    small_icon: Url | None = Field(None, alias="smallicon", description="Status Bar Icon URL")
    priority: int | None = Field(None, ge=-2, le=2, description="control how your notification is displayed")
    group: str | None = Field(None, description="allows you to join notifications in different groups")
    image: Url | None = Field(None, description="Notification image URL")

    @model_validator(mode="after")
    def _check_sms(self):
        self.require_dependencies({"sms_text": ["sms_number"], "call_number": ["sms_number"]})
        if self.is_set("sms_number") and not (self.is_set("sms_text") or self.is_set("mms_file")):
            raise PydanticCustomError("sms_content", "Must use either 'smstext' or 'mmsfile' with 'smsnumber'")
        return self


class JoinMixin:
    """Shared resources between :class:`Join` and :class:`JoinDevices`"""

    name = "join"
    base_url = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1"

    @staticmethod
    def _join_request(url: str, data: dict) -> tuple:
        # Can 't use generic requests util since API doesn't always return error status
        errors = None
        try:
            response = requests.get(url, params=data)
            response.raise_for_status()
            rsp = response.json()
            if not rsp["success"]:
                errors = [rsp["errorMessage"]]
        except requests.RequestException as e:
            if e.response is not None:
                response = e.response
                try:
                    errors = [response.json()["errorMessage"]]
                except json.decoder.JSONDecodeError:
                    errors = [response.text]
            else:
                response = None
                errors = [str(e)]

        return response, errors


class JoinDevices(JoinMixin, ProviderResource):
    """Return a list of Join devices IDs"""

    resource_name = "devices"
    devices_url = "/listDevices"
    schema_model = JoinDevicesSchema

    def _get_resource(self, data: dict):
        url = self.base_url + self.devices_url
        response, errors = self._join_request(url, data)
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return response.json()["records"]


class Join(JoinMixin, Provider):
    """Send Join notifications"""

    push_url = "/sendPush"
    site_url = "https://joaoapps.com/join/api/"

    _resources = {"devices": JoinDevices()}

    schema_model = JoinSchema

    def _prepare_data(self, data: dict) -> dict:
        if data.get("deviceIds"):
            data["deviceIds"] = list_to_commas(data["deviceIds"])
        if data.get("deviceNames"):
            data["deviceNames"] = list_to_commas(data["deviceNames"])
        data["text"] = data.pop("message")
        return data

    def _send_notification(self, data: dict) -> Response:
        # Can 't use generic requests util since API doesn't always return error status
        url = self.base_url + self.push_url
        response, errors = self._join_request(url, data)
        return self.create_response(data, response, errors)
