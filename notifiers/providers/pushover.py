from ..core import Provider, Response
from ..utils import requests
from ..utils.json_schema import one_or_more, list_to_commas


class Pushover(Provider):
    """Send Pushover notifications"""
    base_url = 'https://api.pushover.net/1/messages.json'
    site_url = 'https://pushover.net/'
    name = 'pushover'

    # todo move to be resource
    __sounds = ['pushover', 'bike', 'bugle', 'cashregister', 'classical', 'cosmic', 'falling', 'gamelan', 'incoming',
                'intermission', 'magic', 'mechanical', 'pianobar', 'siren', 'spacealarm', 'tugboat', 'alien', 'climb',
                'persistent', 'echo', 'updown', 'none']
    _required = {'required': ['user', 'message', 'token']}
    _schema = {
        'type': 'object',
        'properties': {
            'user': one_or_more({
                'type': 'string',
                'title': 'the user/group key (not e-mail address) of your user (or you)'
            }),
            'message': {
                'type': 'string',
                'title': 'your message'
            },
            'title': {
                'type': 'string',
                'title': "your message's title, otherwise your app's name is used"
            },
            'token': {
                'type': 'string',
                'title': "your application's API token"
            },
            'device': one_or_more({
                'type': 'string',
                'title': "your user's device name to send the message directly to that device"
            }),
            'priority': {
                'type': 'integer',
                'minimum': -2,
                'maximum': 2,
                'title': 'notification priority'
            },
            'url': {
                'type': 'string',
                'format': 'uri',
                'title': 'a supplementary URL to show with your message'
            },
            'url_title': {
                'type': 'string',
                'title': 'a title for your supplementary URL, otherwise just the URL is shown'
            },
            'sound': {
                'type': 'string',
                'title': "the name of one of the sounds supported by device clients to override the "
                         "user's default sound choice",
                'enum': __sounds
            },
            'timestamp': {
                'type': 'integer',
                'minimum': 0,
                'title': "a Unix timestamp of your message's date and time to display to the user, "
                         "rather than the time your message is received by our API"
            },
            'retry': {
                'type': 'integer',
                'minimum': 30,
                'title': 'how often (in seconds) the Pushover servers will send the same notification to the '
                         'user. priority must be set to 2'
            },
            'expire': {
                'type': 'integer',
                'maximum': 86400,
                'title': 'how many seconds your notification will continue to be retried for. '
                         'priority must be set to 2'
            },
            'callback': {
                'type': 'string',
                'format': 'uri',
                'title': 'a publicly-accessible URL that our servers will send a request to when the user'
                         ' has acknowledged your notification. priority must be set to 2'
            },
            'html': {
                'type': 'boolean',
                'title': 'enable HTML formatting'
            }
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        data['user'] = list_to_commas(data['user'])
        if data.get('device'):
            data['device'] = list_to_commas(data['device'])
        if data.get('html') is not None:
            data['html'] = int(data['html'])
        return data

    def _send_notification(self, data: dict) -> Response:
        path_to_errors = 'errors',
        response, errors = requests.post(self.base_url, data=data, path_to_errors=path_to_errors)
        return self.create_response(data, response, errors)

    @property
    def metadata(self) -> dict:
        m = super().metadata
        m['sounds'] = self.__sounds
        return m

    # todo create devices method
