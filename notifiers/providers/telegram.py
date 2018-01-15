from ..core import Provider, Response
from ..utils import requests


class Telegram(Provider):
    """Send Telegram notifications"""
    base_url = 'https://api.telegram.org/bot{token}/{method}'
    name = 'telegram'
    site_url = 'https://core.telegram.org/'
    path_to_errors = 'description',

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
        url = self.base_url.format(token=token, method='sendMessage')
        response, errors = requests.post(url, json=data, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)

    def updates(self, token) -> list:
        """
        Get a list of updates for the bot token, lets you see the relevant chat IDs

        :param token: Bot token
        :return: List of updates
        """
        url = self.base_url.format(token=token, method='getUpdates')
        response, errors = requests.get(url, path_to_errors=self.path_to_errors)
        self.create_response(response=response, errors=errors).raise_on_errors()
        return response.json()['result']
