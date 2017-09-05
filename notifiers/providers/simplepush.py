import requests

from ..core import Provider, Response
from ..utils.helpers import create_response


class SimplePush(Provider):
    base_url = 'https://api.simplepush.io/send'
    site_url = 'https://simplepush.io/'
    provider_name = 'simplepush'

    @property
    def schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'key': {'type': 'string',
                        'title': 'your user key'},
                'message': {'type': 'string',
                            'title': 'your message'},
            },
            'required': ['key', 'message'],
            'additionalProperties': False
        }

    def _prepare_data(self, data: dict) -> dict:
        data['msg'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        try:
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            if e.response is not None:
                response = e.response
                errors = [response.json()['message']]
            else:
                response = None
                errors = (str(e))
            return create_response(provider_name=self.provider_name, data=data, response=response, failed=True,
                                   errors=errors)

        return create_response(provider_name=self.provider_name, data=data, response=response)
