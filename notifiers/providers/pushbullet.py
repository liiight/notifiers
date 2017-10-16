import requests

from ..core import Provider, Response
from ..utils.helpers import create_response


class Pushbullet(Provider):
    base_url = 'https://api.pushbullet.com/v2/pushes'
    site_url = 'https://www.pushbullet.com'
    provider_name = 'pushbullet'

    @property
    def schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'title': 'Body of the push'
                },
                'token': {
                    'type': 'string',
                    'title': 'API access token'
                },
                'title': {
                    'type': 'string',
                    'title': 'Title of the push'
                },
                'type': {
                    'type': 'string',
                    'title': 'Type of the push, one of "note" or "link"',
                    'enum': ['note', 'link']
                },
                'url': {
                    'type': 'string',
                    'title': 'URL field, used for type="link" pushes'
                },
                'source_device_iden': {
                    'type': 'string',
                    'title': 'Device iden of the sending device'
                },
                'device_iden': {
                    'type': 'string',
                    'title': 'Device iden of the target device, if sending to a single device'
                },
                'client_iden': {
                    'type': 'string',
                    'title': 'Client iden of the target client, sends a push to all users who have granted access to '
                             'this client. The current user must own this client'
                },
                'channel_tag': {
                    'type': 'string',
                    'title': 'Channel tag of the target channel, sends a push to all people who are subscribed to '
                             'this channel. The current user must own this channel.'
                },
                'email': {
                    'type': 'string',
                    'title': 'Email address to send the push to. If there is a pushbullet user with this address,'
                             ' they get a push, otherwise they get an email'
                },
                'guid': {
                    'type': 'string',
                    'title': 'Unique identifier set by the client, used to identify a push in case you receive it '
                             'from /v2/everything before the call to /v2/pushes has completed. This should be a unique'
                             ' value. Pushes with guid set are mostly idempotent, meaning that sending another push '
                             'with the same guid is unlikely to create another push (it will return the previously'
                             ' created push).'
                }
            },
            'required': ['message', 'token'],
            'additionalProperties': False
        }

    @property
    def defaults(self) -> dict:
        return {
            'type': 'note'
        }

    def _prepare_data(self, data: dict) -> dict:
        data['body'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        response_data = {
            'provider_name': self.provider_name,
            'data': data
        }
        headers = {
            'access-token': data.pop('token')
        }
        try:
            response = requests.post(self.base_url, json=data, headers=headers)
            response.raise_for_status()
            response_data['response'] = response
        except requests.RequestException as e:
            if e.response is not None:
                response_data['response'] = e.response
                response_data['errors'] = [e.response.json()['error']['message']]
            else:
                response_data['errors'] = [(str(e))]
        return create_response(**response_data)
