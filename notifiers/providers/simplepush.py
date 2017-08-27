import requests

from ..core import Provider, Response


class SimplePush(Provider):
    base_url = 'https://api.simplepush.io/send'
    site_url = 'https://simplepush.io/'
    provider_name = 'simplepush'

    @property
    def schema(self):
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

    def _prepare_data(self, data: dict):
        data['msg'] = data.pop('message')
        return data

    def _send_notification(self, data):
        status = 'Success'
        errors = []
        response = None
        try:
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            status = 'Failure'
            if e.response is not None:
                response = e.response
                errors = [response.json()['message']]
            else:
                errors.append(str(e))
        finally:
            return Response(status=status,
                            provider=self.provider_name,
                            data=data,
                            response=response,
                            errors=errors)
