import requests

from ..core import Provider, Response
from ..exceptions import NotifierException


class Gitter(Provider):
    """Send Gitter notifications"""
    base_url = 'https://api.gitter.im/v1/rooms'
    message_url = base_url + '/{room_id}/chatMessages'
    site_url = 'https://gitter.im'
    name = 'gitter'

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
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            errors = None
        except requests.RequestException as e:
            if e.response is not None:
                response = e.response
                errors = [e.response.json()['error']]
            else:
                response = None
                errors = [(str(e))]
        return self.create_response(data, response, errors)

    def rooms(self, token: str, query: str = None) -> list:
        """
        Return a list of available Gitter rooms. If query param is sent, filters the list according to it

        :param token: App token
        :param query: Optional query string
        :return: List of room IDs
        """
        try:
            headers = self._get_headers(token)
            params = {'q': query} if query else {}
            rsp = requests.get(self.base_url, headers=headers, params=params)
            rsp.raise_for_status()
            return rsp.json()['results'] if query else rsp.json()
        except requests.RequestException as e:
            message = e.response.json()['error']
            raise NotifierException(provider=self.name, message=message)
