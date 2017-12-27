import requests

from ..core import Provider, Response
from ..utils.helpers import create_response


class SimplePush(Provider):
    base_url = 'https://api.simplepush.io/send'
    site_url = 'https://simplepush.io/'
    provider_name = 'simplepush'

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
        response_data = {
            'provider_name': self.provider_name,
            'data': data
        }
        try:
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
            response_data['response'] = response
        except requests.RequestException as e:
            if e.response is not None:
                response_data['response'] = e.response
                response_data['errors'] = [e.response.json()['message']]
            else:
                response_data['errors'] = [(str(e))]
        return create_response(**response_data)
