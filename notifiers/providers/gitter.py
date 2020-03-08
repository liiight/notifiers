from urllib.parse import urljoin

from pydantic import Field

from ..exceptions import ResourceError
from ..models.provider import Provider
from ..models.provider import ProviderResource
from ..models.provider import ResourceSchema
from ..models.response import Response
from ..utils import requests


class GitterSchemaBase(ResourceSchema):
    token: str = Field(..., description="Access token")

    @property
    def auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}


class GitterRoomSchema(GitterSchemaBase):
    """List rooms the current user is in"""

    filter: str = Field(None, description="Filter results")


class GitterSchema(GitterSchemaBase):
    """Send a message to a room"""

    message: str = Field(..., description="Body of the message", alias="text")
    room_id: str = Field(..., description="ID of the room to send the notification to")
    status: bool = Field(
        None, description="set to true to indicate that the message is a status update"
    )


class GitterMixin:
    """Shared attributes between :class:`~notifiers.providers.gitter.GitterRooms` and
    :class:`~notifiers.providers.gitter.Gitter`"""

    name = "gitter"
    path_to_errors = "errors", "error"
    base_url = "https://api.gitter.im/v1/rooms"


class GitterRooms(GitterMixin, ProviderResource):
    """Returns a list of Gitter rooms via token"""

    resource_name = "rooms"
    schema_model = GitterRoomSchema

    def _get_resource(self, data: GitterRoomSchema) -> list:
        params = {}
        if data.filter:
            params["q"] = data.filter

        response, errors = requests.get(
            self.base_url,
            headers=data.auth_header,
            params=params,
            path_to_errors=self.path_to_errors,
        )
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        rsp = response.json()
        return rsp["results"] if data.filter else rsp


class Gitter(GitterMixin, Provider):
    """Send Gitter notifications"""

    site_url = "https://gitter.im"
    schema_model = GitterSchema

    _resources = {"rooms": GitterRooms()}

    def _send_notification(self, data: GitterSchema) -> Response:
        url = urljoin(self.base_url, f"/{data.room_id}/chatMessages")

        payload = data.to_dict(include={"message", "status"})
        response, errors = requests.post(
            url,
            json=payload,
            headers=data.auth_header,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(payload, response, errors)
