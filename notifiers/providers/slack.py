from ..core import Provider, Response
from ..utils import requests


class Slack(Provider):
    """Send Slack webhook notifications"""
    base_url = 'https://hooks.slack.com/services/'
    site_url = 'https://api.slack.com/incoming-webhooks'
    name = 'slack'

    __fields = {
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
                    'title': 'Text value of the field. May contain standard message markup and must'
                             ' be escaped as normal. May be multi-line'
                },
                'short': {
                    'type': 'boolean',
                    'title': 'Optional flag indicating whether the `value` is short enough to be displayed'
                             ' side-by-side with other values'
                }
            },
            'required': ['title'],
            'additionalProperties': False
        }
    }
    __attachments = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'title': 'Attachment title'
                },
                'author_name': {
                    'type': 'string',
                    'title': "Small text used to display the author's name"
                },
                'author_link': {
                    'type': 'string',
                    'title': 'A valid URL that will hyperlink the author_name text mentioned above. '
                             'Will only work if author_name is present'
                },
                'author_icon': {
                    'type': 'string',
                    'title': 'A valid URL that displays a small 16x16px image to the left of the author_name text. '
                             'Will only work if author_name is present'
                },
                'title_link': {
                    'type': 'string',
                    'title': 'Attachment title URL'
                },
                'image_url': {
                    'type': 'string',
                    'title': 'Image URL'
                },
                'thumb_url': {
                    'type': 'string',
                    'title': 'Thumbnail URL'
                },
                'footer': {
                    'type': 'string',
                    'title': 'Footer text'
                },
                'footer_icon': {
                    'type': 'string',
                    'title': 'Footer icon URL'
                },
                'ts': {
                    'type': 'integer',
                    'title': 'Provided timestamp (epoch)'
                },
                'fallback': {
                    'type': 'string',
                    'title': "A plain-text summary of the attachment. This text will be used in clients that don't"
                             " show formatted text (eg. IRC, mobile notifications) and should not contain any markup."
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
                    'title': "Can either be one of 'good', 'warning', 'danger', or any hex color code"
                },
                'fields': __fields
            },
            'required': ['fallback'],
            'additionalProperties': False
        }
    }
    _required = {
        'required':
            [
                'webhook_url',
                'message'
            ]
    }
    _schema = {
        'type': 'object',
        'properties': {
            'webhook_url': {
                'type': 'string',
                'title': 'the webhook URL to use. Register one at https://my.slack.com/services/new/incoming-webhook/'
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
            'attachments': __attachments
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        text = data.pop('message')
        data['text'] = text
        if data.get('icon_emoji'):
            icon_emoji = data['icon_emoji']
            if not icon_emoji.startswith(':'):
                icon_emoji = f':{icon_emoji}'
            if not icon_emoji.endswith(':'):
                icon_emoji += ':'
            data['icon_emoji'] = icon_emoji
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop('webhook_url')
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
