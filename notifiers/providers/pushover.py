import requests

from ..core import Provider, NotificationResponse
from ..utils.json_schema import one_or_more


class Pushover(Provider):
    base_url = 'https://api.pushover.net/1/messages.json'
    provider_name = 'pushover'

    schema = {
        'type': 'object',
        'properties': {
            'user': {'type': 'string'},
            'message': {'type': 'string'},
            'title': {'type': 'string'},
            'token': {'type': 'string'},
            'device': one_or_more({'type': 'string'}),
            'priority': {'oneOf': [
                {'type': 'number', 'minimum': -2, 'maximum': 2},
                {'type': 'string'}]},
            'url': {'type': 'string', 'format': 'uri'},
            'url_title': {'type': 'string'},
            'sound': {'type': 'string'},
            'retry': {'type': 'integer', 'minimum': 30},
            'expire': {'type': 'integer', 'maximum': 86400},
            'callback': {'type': 'string', 'format': 'uri'},
            'html': {'type': 'integer', 'minimum': 0, 'maximum': 1}
        },
        'required': ['user', 'message', 'token'],
        'additionalProperties': False
    }

    def _prepare_data(self, data):
        if isinstance(data.get('device'), list):
            data['device'] = ','.join(data['device'])
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
                errors = response.json()['errors']
            else:
                errors.append(str(e))
        finally:
            return NotificationResponse(status=status,
                                        provider=self.provider_name,
                                        data=data,
                                        response=response,
                                        errors=errors)
