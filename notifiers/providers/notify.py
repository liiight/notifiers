from ..core import Provider
from ..core import Response
from ..utils import requests


class NotifyMixin:
    name = "notify"
    site_url = "https://github.com/K0IN/Notify"
    base_url = "{base_url}/api/notify"
    path_to_errors = ("message",)

    def _get_headers(self, token: str) -> dict:
        """
        Builds Notify's requests header bases on the token provided

        :param token: Send token
        :return: Authentication header dict
        """
        return {"Authorization": f"Bearer {token}"}


class Notify(NotifyMixin, Provider):
    """Send Notify notifications"""

    site_url = "https://github.com/K0IN/Notify"
    name = "notify"

    _required = {"required": ["title", "message", "base_url"]}
    _schema = {
        "type": "object",
        "properties": {
            "base_url": {"type": "string"},
            "message": {"type": "string", "title": "your message"},
            "title": {"type": "string", "title": "your message's title"},
            "token": {
                "type": "string",
                "title": "your application's send key, see https://github.com/K0IN/Notify/blob/main/doc/docker.md",
            },
            "tags": {
                "type": "array",
                "title": "your message's tags",
                "items": {"type": "string"},
            },
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        return data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url.format(base_url=data.pop("base_url"))
        token = data.pop("token", None)
        headers = self._get_headers(token) if token else {}
        response, errors = requests.post(
            url,
            json={
                "message": data.pop("message"),
                "title": data.pop("title", None),
                "tags": data.pop("tags", []),
            },
            headers=headers,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(data, response, errors)
