import requests

from ..exceptions import NotificationError
from ..core import NotificationProvider, NotificationResponse
from ..utils.json_schema import one_or_more, list_to_commas


class Pushover(NotificationProvider):
    base_url = 'https://api.pushover.net/1/messages.json'
    site_url = 'https://pushover.net/'
    provider_name = 'pushover'
    sounds_url = 'https://api.pushover.net/1/sounds.json?token={}'

    schema = {
        'type': 'object',
        'properties': {
            'user': one_or_more({'type': 'string',
                                 'title': 'the user/group key (not e-mail address) of your user (or you)'}),
            'message': {'type': 'string',
                        'title': 'your message'},
            'title': {'type': 'string',
                      'title': 'your message\'s title, otherwise your app\'s name is used'},
            'token': {'type': 'string',
                      'title': 'your application\'s API token'},
            'device': one_or_more({'type': 'string',
                                   'title': 'your user\'s device name to send the message directly to that device'}),
            'priority': {'oneOf': [
                {'type': 'number', 'minimum': -2, 'maximum': 2},
                {'type': 'string'}],
                'title': 'notification priority'},
            'url': {'type': 'string',
                    'format': 'uri',
                    'title': 'a supplementary URL to show with your message'},
            'url_title': {'type': 'string',
                          'title': 'a title for your supplementary URL, otherwise just the URL is shown'},
            'sound': {'type': 'string',
                      'title': 'the name of one of the sounds supported by device clients to override the '
                               'user\'s default sound choice'},
            'timestamp': {'type': 'integer',
                          'minimum': 0,
                          'title': 'a Unix timestamp of your message\'s date and time to display to the user, '
                                   'rather than the time your message is received by our API'},
            'retry': {'type': 'integer',
                      'minimum': 30,
                      'title': 'how often (in seconds) the Pushover servers will send the same notification to the '
                               'user. priority must be set to 2'},
            'expire': {'type': 'integer',
                       'maximum': 86400,
                       'title': 'how many seconds your notification will continue to be retried for. '
                                'priority must be set to 2'},
            'callback': {'type': 'string',
                         'format': 'uri',
                         'title': 'a publicly-accessible URL that our servers will send a request to when the user'
                                  ' has acknowledged your notification. priority must be set to 2'},
            'html': {'type': 'integer',
                     'minimum': 0,
                     'maximum': 1,
                     'title': 'enable HTML formatting'}
        },
        'required': ['user', 'message', 'token'],
        'additionalProperties': False
    }

    def _prepare_data(self, data):
        data['user'] = list_to_commas(data['user'])
        if data.get('device'):
            data['device'] = list_to_commas(data['device'])
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

    def sounds(self, token):
        url = self.sounds_url.format(token)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            errors = []
            if e.response is not None:
                errors = e.response.json()['errors']
            raise NotificationError(provider=self.provider_name, message='Could not retrieve sounds', errors=errors)
