import requests

from ..core import Provider, Response
from ..utils.helpers import create_response
from ..exceptions import NotifierException


class Telegram(Provider):
    base_url = 'https://api.telegram.org/bot{token}/{method}'
    provider_name = 'telegram'
    site_url = 'https://core.telegram.org/'

    @property
    def schema(self) -> dict:
        return {
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
                    'type': [
                        'string',
                        'integer'
                    ],
                    'title': 'Unique identifier for the target chat or username of the target channel '
                             '(in the format @channelusername)'
                },
                'parse_mode': {
                    'type': 'string',
                    'title': 'Send Markdown or HTML, if you want Telegram apps to show bold, italic,'
                             ' fixed-width text or inline URLs in your bot\'s message.',
                    'enum': [
                        'markdown',
                        'html'
                    ]
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
            'required': ['message', 'chat_id', 'token'],
            'additionalProperties': False
        }

    def _prepare_data(self, data: dict) -> dict:
        data['text'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        token = data.pop('token')
        url = self.base_url.format(token=token, method='sendMessage')
        response_data = {
            'provider_name': self.provider_name,
            'data': data
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            response_data['response'] = response
        except requests.RequestException as e:
            if e.response is not None:
                response_data['response'] = e.response
                response_data['errors'] = [e.response.json()['description']]
            else:
                response_data['errors'] = [(str(e))]
        return create_response(**response_data)

    def updates(self, token) -> list:
        """
        Get a list of updates for the bot token, lets you see the relevant chat IDs

        :param token: Bot token
        :return: List of updates
        """
        url = self.base_url.format(token=token, method='getUpdates')
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()['result']
        except requests.RequestException as e:
            message = e.response.json()['description']
            raise NotifierException(provider=self.provider_name, message=message)
