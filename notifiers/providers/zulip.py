import requests

from ..core import Provider, Response
from ..exceptions import NotifierException


class Zulip(Provider):
    """Send Zulip notifications"""
    name = 'zulip'
    site_url = 'https://zulipchat.com/api/'
    api_endpoint = '/api/v1/messages'
    base_url = 'https://{domain}.zulipchat.com'

    __type = {
        'type': 'string',
        'enum': ['stream', 'private'],
        'title': 'Type of message to send'
    }
    _required = {
        'allOf': [
            {'required': ['message', 'email', 'api_key', 'to']},
            {'oneOf': [
                {'required': ['domain']},
                {'required': ['server']}
            ],
                'error_oneOf': "Only one of 'domain' or 'server' is allowed"
            }
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'Message content'
            },
            'email': {
                'type': 'string',
                'title': 'User email'
            },
            'api_key': {
                'type': 'string',
                'title': 'User API Key'
            },
            'type': __type,
            'type_': __type,
            'to': {
                'type': 'string',
                'title': 'Target of the message'
            },
            'subject': {
                'type': 'string',
                'title': 'Title of the stream message. Required when using stream.'
            },
            'domain': {
                'type': 'string',
                'title': 'Zulip cloud domain'
            },
            'server': {
                'type': 'string',
                'title': 'Zulip server URL. Example: https://myzulip.server.com'
            }
        },
        'additionalProperties': False
    }

    @property
    def defaults(self) -> dict:
        return {
            'type': 'stream'
        }

    def _prepare_data(self, data: dict) -> dict:
        base_url = self.base_url.format(domain=data.pop('domain')) if data.get('domain') else data.pop('server')
        data['url'] = base_url + self.api_endpoint
        data['content'] = data.pop('message')
        # A workaround since `type` is a reserved word
        if data.get('type_'):
            data['type'] = data.pop('type_')
        return data

    def _validate_data_dependencies(self, data: dict) -> dict:
        if data['type'] == 'stream' and not data.get('subject'):
            raise NotifierException(provider=self.name,
                                    message="'subject' is required when 'type' is 'stream'",
                                    data=data)
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop('url')
        auth = (data.pop('email'), data.pop('api_key'))
        errors = None
        try:
            response = requests.post(url, data=data, auth=auth)
            response.raise_for_status()
        except requests.RequestException as e:
            if e.response is not None:
                response = e.response
                errors = [e.response.json()['msg']]
            else:
                response = None
                errors = [(str(e))]
        return self.create_response(data, response, errors)
