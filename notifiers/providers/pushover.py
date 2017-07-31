import maya
import requests

from notifiers.exceptions import NotificationError
from notifiers.notifier import Notifier
from notifiers.utils.json_schema import one_or_more


class Pushover(Notifier):
    base_url = 'https://api.pushover.net/1/messages.json'

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
            'url': {'type': 'string'},
            'url_title': {'type': 'string'},
            'sound': {'type': 'string'},
            'retry': {'type': 'integer', 'minimum': 30},
            'expire': {'type': 'integer', 'maximum': 86400},
            'callback': {'type': 'string', 'format': 'uri'},
            'html': {'type': 'boolean'}
        },
        'required': ['user', 'message', 'token'],
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        device = data.get('device')
        if device and isinstance(device, list):
            data['device'] = ','.join(device)
        if data.get('html'):
            data['html'] = 1
        return data

    def _send_notification(self, data: dict):
        try:
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 429:
                    reset_time = maya.parse(e.response.headers['X-Limit-App-Reset']).iso8601()
                    error_message = f'Monthly pushover message limit reached. Next reset: {reset_time}'
                else:
                    error_message = e.response.json()['errors'][0]
            else:
                error_message = str(e)
            raise NotificationError(error_message)
