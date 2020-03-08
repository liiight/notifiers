from enum import Enum
from functools import partial
from mimetypes import guess_type

from pydantic import EmailStr
from pydantic import Field
from pydantic import FilePath
from pydantic import HttpUrl
from pydantic import root_validator

from ..exceptions import ResourceError
from ..models.provider import Provider
from ..models.provider import ProviderResource
from ..models.provider import ResourceSchema
from ..models.response import Response
from ..utils import requests


class PushbulletType(Enum):
    note = "note"
    file = "file"
    link = "link"


class PushbulletBaseSchema(ResourceSchema):
    token: str = Field(..., description="API access token")


class PushbulletSchema(PushbulletBaseSchema):
    type: PushbulletType = Field(PushbulletType.note, description="Type of the push")
    message: str = Field(
        ..., description="Body of the push, used for all types of pushes", alias="body"
    )
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

    @root_validator(skip_on_failure=True)
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
    schema_model = PushbulletBaseSchema

    def _get_resource(self, data: PushbulletBaseSchema) -> list:
        headers = self._get_headers(data.token)
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
    upload_request = "https://api.pushbullet.com/v2/upload-request"
    site_url = "https://www.pushbullet.com"

    _resources = {"devices": PushbulletDevices()}
    schema_model = PushbulletSchema

    def _upload_file(self, file: FilePath, headers: dict) -> dict:
        """Fetches an upload URL and upload the content of the file"""
        data = {"file_name": file.name, "file_type": guess_type(str(file))[0]}
        response, errors = requests.post(
            self.upload_request,
            json=data,
            headers=headers,
            path_to_errors=self.path_to_errors,
        )
        error = partial(
            ResourceError,
            errors=errors,
            resource="pushbullet_file_upload",
            provider=self.name,
            data=data,
            response=response,
        )
        if errors:
            raise error()
        file_data = response.json()
        files = requests.file_list_for_request(
            file, "file", mimetype=file_data["file_type"]
        )
        response, errors = requests.post(
            file_data.pop("upload_url"),
            files=files,
            headers=headers,
            path_to_errors=self.path_to_errors,
        )
        if errors:
            raise error()

        return file_data

    def _send_notification(self, data: PushbulletSchema) -> Response:
        request_data = data.to_dict()
        headers = self._get_headers(request_data.pop("token"))
        if data.file:
            request_data.update(self._upload_file(data.file, headers))
        response, errors = requests.post(
            self.base_url,
            json=request_data,
            headers=headers,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(request_data, response, errors)
