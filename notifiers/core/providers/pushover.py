import maya
import requests

from ..exceptions import NotificationError
from ..provider import Provider
from ..utils.json_schema import one_or_more

__all__ = ['Pushover']


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

    def _prepare_data(self, data: dict) -> dict:
        if isinstance(data.get('device'), list):
            data['device'] = ','.join(data['device'])
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
