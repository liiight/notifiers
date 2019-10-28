from ..core import Provider
from ..core import ProviderResource
from ..core import Response
from ..exceptions import ResourceError
from ..utils import requests


class GitterMixin:
    """Shared attributes between :class:`~notifiers.providers.gitter.GitterRooms` and
    :class:`~notifiers.providers.gitter.Gitter`"""

    name = "gitter"
    path_to_errors = "errors", "error"
    base_url = "https://api.gitter.im/v1/rooms"

    def _get_headers(self, token: str) -> dict:
        """
        Builds Gitter requests header bases on the token provided

        :param token: App token
        :return: Authentication header dict
        """
        return {"Authorization": f"Bearer {token}"}


class GitterRooms(GitterMixin, ProviderResource):
    """Returns a list of Gitter rooms via token"""

    resource_name = "rooms"

    _required = {"required": ["token"]}

    _schema = {
        "type": "object",
        "properties": {
            "token": {"type": "string", "title": "access token"},
            "filter": {"type": "string", "title": "Filter results"},
        },
        "additionalProperties": False,
    }

    def _get_resource(self, data: dict) -> list:
        headers = self._get_headers(data["token"])
        filter_ = data.get("filter")
        params = {"q": filter_} if filter_ else {}
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
        return rsp["results"] if filter_ else rsp


class Gitter(GitterMixin, Provider):
    """Send Gitter notifications"""

    message_url = "/{room_id}/chatMessages"
    site_url = "https://gitter.im"

    _resources = {"rooms": GitterRooms()}

    _required = {"required": ["message", "token", "room_id"]}
    _schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "title": "Body of the message"},
            "token": {"type": "string", "title": "access token"},
            "room_id": {
                "type": "string",
                "title": "ID of the room to send the notification to",
            },
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        data["text"] = data.pop("message")
        return data

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata["message_url"] = self.message_url
        return metadata

    def _send_notification(self, data: dict) -> Response:
        room_id = data.pop("room_id")
        url = self.base_url + self.message_url.format(room_id=room_id)

        headers = self._get_headers(data.pop("token"))
        response, errors = requests.post(
            url, json=data, headers=headers, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
