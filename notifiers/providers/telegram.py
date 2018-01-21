from ..core import Provider, Response, ProviderResource
from ..exceptions import ResourceError
from ..utils import requests


class TelegramProxy:
    """Shared resources between :class:`TelegramUpdates` and :class:`Telegram`"""
    base_url = 'https://api.telegram.org/bot{token}'
    name = 'telegram'
    path_to_errors = 'description',


class TelegramUpdates(TelegramProxy, ProviderResource):
    """Return Telegram bot updates, correlating to the `getUpdates` method. Returns chat IDs needed to notifications"""
    resource_name = 'updates'
    updates_endpoint = '/getUpdates'

    _required = {
        'required': [
            'token'
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'token': {
                'type': 'string',
                'title': 'Bot token'
            }
        },
        'additionalProperties': False
    }

    def _get_resource(self, data: dict) -> list:
        url = self.base_url.format(token=data['token']) + self.updates_endpoint
        response, errors = requests.get(url, path_to_errors=self.path_to_errors)
        if errors:
            raise ResourceError(errors=errors,
                                resource=self.resource_name,
                                provider=self.name,
                                data=data,
                                response=response)
        return response.json()['result']


class Telegram(TelegramProxy, Provider):
    """Send Telegram notifications"""

    site_url = 'https://core.telegram.org/'
    push_endpoint = '/sendMessage'

    _required = {'required': ['message', 'chat_id', 'token']}
    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'Text of the message to be sent'
            },
            'token': {
                'type': 'string',
                'title': 'Bot token'
            },
            'chat_id': {
                'oneOf': [
                    {'type': 'string'},
                    {'type': 'integer'}
                ],
                'title': 'Unique identifier for the target chat or username of the target channel '
                         '(in the format @channelusername)'
            },
            'parse_mode': {
                'type': 'string',
                'title': "Send Markdown or HTML, if you want Telegram apps to show bold, italic,"
                         " fixed-width text or inline URLs in your bot's message.",
                'enum': ['markdown', 'html']
            },
            'disable_web_page_preview': {
                'type': 'boolean',
                'title': 'Disables link previews for links in this message'
            },
            'disable_notification': {
                'type': 'boolean',
                'title': 'Sends the message silently. Users will receive a notification with no sound.'
            },
            'reply_to_message_id': {
                'type': 'integer',
                'title': 'If the message is a reply, ID of the original message'
            }
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        data['text'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        token = data.pop('token')
        url = self.base_url.format(token=token) + self.push_endpoint
        response, errors = requests.post(url, json=data, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)

    @property
    def resources(self):
        return [
            'updates'
        ]

    @property
    def updates(self) -> TelegramUpdates:
        return TelegramUpdates()
