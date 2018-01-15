from ..core import Provider, Response
from ..utils import requests


class Gitter(Provider):
    """Send Gitter notifications"""
    base_url = 'https://api.gitter.im/v1/rooms'
    message_url = base_url + '/{room_id}/chatMessages'
    site_url = 'https://gitter.im'
    name = 'gitter'
    path_to_errors = 'errors',

    _required = {'required': ['message', 'token', 'room_id']}
    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'Body of the message'
            },
            'token': {
                'type': 'string',
                'title': 'access token'
            },
            'room_id': {
                'type': 'string',
                'title': 'ID of the room to send the notification to'
            }
        },
        'required': ['message', 'token', 'room_id'],
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        data['text'] = data.pop('message')
        return data

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata['message_url'] = self.message_url
        return metadata

    def _get_headers(self, token: str) -> dict:
        """
        Builds Gitter requests header bases on the token provided

        :param token: App token
        :return: Authentication header dict
        """
        return {'Authorization': f'Bearer {token}'}

    def _send_notification(self, data: dict) -> Response:
        room_id = data.pop('room_id')
        url = self.message_url.format(room_id=room_id)

        headers = self._get_headers(data.pop('token'))
        response, errors = requests.post(url, json=data, headers=headers, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)

    def rooms(self, token: str, query: str = None) -> list:
        """
        Return a list of available Gitter rooms. If query param is sent, filters the list according to it

        :param token: App token
        :param query: Optional query string
        :return: List of room IDs
        """
        headers = self._get_headers(token)
        params = {'q': query} if query else {}
        response, errors = requests.get(self.base_url,
                                        headers=headers,
                                        params=params,
                                        path_to_errors=self.path_to_errors)
        self.create_response(response=response, errors=errors).raise_on_errors()
        rsp = response.json()
        return rsp['results'] if query else rsp
