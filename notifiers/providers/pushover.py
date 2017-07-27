import maya
import requests

from notifiers.exceptions import NotificationError
from notifiers.notifier import Notifier
from notifiers.utils.json_schema import one_or_more


class Pushover(Notifier):
    base_url = 'https://api.pushover.net/1/messages.json'
    default_token = 'aPwSHwkLcNaavShxktBpgJH4bRWc3m'

    schema = {
        'type': 'object',
        'properties': {
            'user_key': one_or_more({'type': 'string'}),
            'message': {'type': 'string'},
            'title': {'type': 'string'},
            'token': {'type': 'string', 'default': default_token},
            'device': one_or_more({'type': 'string'}),
            'priority': {'oneOf': [
                {'type': 'number', 'minimum': -2, 'maximum': 2},
                {'type': 'string'}]},
            'url': {'type': 'string'},
            'url_title': {'type': 'string'},
            'sound': {'type': 'string'},
            'retry': {'type': 'integer', 'minimum': 30},
            'expire': {'type': 'integer', 'maximum': 86400},
            'callback': {'type': 'string'},
            'html': {'type': 'boolean'}
        },
        'required': ['user_key', 'message', 'title'],
        'additionalProperties': False
    }

    def _send_notification(self, data):
        try:
            response = requests.post(self.base_url, data=data)
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
