import requests

from ..core import Provider, Response
from ..utils.helpers import create_response


class Slack(Provider):
    base_url = 'https://hooks.slack.com/services/'
    site_url = 'https://api.slack.com/incoming-webhooks'
    provider_name = 'slack'

    @property
    def schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'webhook_url': {
                    'type': 'string',
                    'title': 'the webhook URL to use.'
                             ' Register one at https://my.slack.com/services/new/incoming-webhook/'
                },
                'icon_url': {
                    'type': 'string',
                    'title': 'override bot icon with image URL'
                },
                'icon_emoji': {
                    'type': 'string',
                    'title': 'override bot icon with emoji name.'
                },
                'username': {
                    'type': 'string',
                    'title': 'override the displayed bot name'
                },
                'channel': {
                    'type': 'string',
                    'title': 'override default channel or private message'
                },
                'unfurl_links': {
                    'type': 'boolean',
                    'title': 'avoid automatic attachment creation from URLs'
                },
                'message': {
                    'type': 'string',
                    'title': 'This is the text that will be posted to the channel'
                },
                'attachments': {
                    'type': 'object',
                    'properties': {
                        'fallback': {
                            'type': 'string',
                            'title': 'Required text summary of the attachment that is shown by clients that understand attachments but choose not to show them'
                        },
                        'text': {
                            'type': 'string',
                            'title': 'Optional text that should appear within the attachment'
                        },
                        'pretext': {
                            'type': 'string',
                            'title': 'Optional text that should appear above the formatted data'
                        },
                        'color': {
                            'type': 'string',
                            'title': 'Can either be one of \'good\', \'warning\', \'danger\', or any hex color code'
                        },
                        'fields': {
                            'type': 'array',
                            'title': 'Fields are displayed in a table on the message',
                            'minItems': 1,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'title': {
                                        'type': 'string',
                                        'title': 'Required Field Title'
                                    },
                                    'value': {
                                        'type': 'string',
                                        'title': 'Text value of the field. May contain standard message markup and must be escaped as normal. May be multi-line'
                                    },
                                    'short': {
                                        'type': 'boolean',
                                        'title': 'Optional flag indicating whether the `value` is short enough to be displayed side-by-side with other values'
                                    }
                                },
                                'required': ['title'],
                                'additionalProperties': False
                            }
                        }
                    },
                    'required': ['fallback'],
                    'additionalProperties': False
                }
            },
            'required': ['webhook_url', 'message'],
            'additionalProperties': False
        }

    def _prepare_data(self, data: dict) -> dict:
        text = data.pop('message')
        data['text'] = text
        if data.get('icon_emoji'):
            icon_emoji = data['icon_emoji']
            if not icon_emoji.startswith(':'):
                icon_emoji = ':' + icon_emoji
            if not icon_emoji.endswith(':'):
                icon_emoji += ':'
            data['icon_emoji'] = icon_emoji
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop('webhook_url')
        response_data = {'provider_name': self.provider_name,
                         'data': data}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            if e.response is not None:
                response_data['response'] = e.response
                response_data['errors'] = [e.response.text]
            else:
                response_data['errors'] = [(str(e))]
        return create_response(**response_data)
