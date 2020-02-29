from urllib.parse import urljoin

from pydantic import Field

from ..exceptions import ResourceError
from ..models.provider import Provider
from ..models.provider import ProviderResource
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests


class GitterSchemaBase(SchemaModel):
    token: str = Field(..., description="Access token")


class GitterRoomSchema(GitterSchemaBase):
    filter: str = Field(None, description="Filter results")


class GitterSchema(GitterSchemaBase):
    text: str = Field(..., description="Body of the message", alias="message")
    room_id: str = Field(..., description="ID of the room to send the notification to")


class GitterMixin:
    """Shared attributes between :class:`~notifiers.providers.gitter.GitterRooms` and
    :class:`~notifiers.providers.gitter.Gitter`"""

    name = "gitter"
    path_to_errors = "errors", "error"
    base_url = "https://api.gitter.im/v1/rooms"

    @staticmethod
    def _get_headers(token: str) -> dict:
        """
        Builds Gitter requests header bases on the token provided

        :param token: App token
        :return: Authentication header dict
        """
        return {"Authorization": f"Bearer {token}"}


class GitterRooms(GitterMixin, ProviderResource):
    """Returns a list of Gitter rooms via token"""

    resource_name = "rooms"
    schema_model = GitterRoomSchema

    def _get_resource(self, data: GitterRoomSchema) -> list:
        headers = self._get_headers(data.token)
        params = {}
        if data.filter:
            params["q"] = data.filter

        response, errors = requests.get(
            self.base_url,
            headers=headers,
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

    message_url = "/{room_id}/chatMessages"
    site_url = "https://gitter.im"
    schema_model = GitterSchema

    _resources = {"rooms": GitterRooms()}

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata["message_url"] = self.message_url
        return metadata

    def _send_notification(self, data: GitterSchema) -> Response:
        data = data.to_dict()
        room_id = data.pop("room_id")
        url = urljoin(self.base_url, self.message_url.format(room_id=room_id))

        headers = self._get_headers(data.pop("token"))
        response, errors = requests.post(
            url, json=data, headers=headers, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
