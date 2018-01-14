import requests

from ..core import Provider, Response
from ..utils.helpers import create_response


class SimplePush(Provider):
    """Send SimplePush notifications"""
    base_url = 'https://api.simplepush.io/send'
    site_url = 'https://simplepush.io/'
    name = 'simplepush'

    _required = {'required': ['key', 'message']}
    _schema = {
        'type': 'object',
        'properties': {
            'key': {
                'type': 'string',
                'title': 'your user key'
            },
            'message': {
                'type': 'string',
                'title': 'your message'
            },
            'title': {
                'type': 'string',
                'title': 'message title'
            },
            'event': {
                'type': 'string',
                'title': 'Event ID'
            },
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        data['msg'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        errors = None
        try:
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            if e.response is not None:
                response = e.response
                errors = [e.response.json()['message']]
            else:
                response = None
                errors = [(str(e))]
        return self.create_response(data, response, errors)
