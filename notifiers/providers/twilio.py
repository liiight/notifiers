from ..core import Provider, Response, ProviderResource
from ..utils.helpers import snake_to_camel_case
from ..utils import requests
from ..exceptions import ResourceError


class Twilio(Provider):
    """Send an SMS via a Twilio number"""
    name = 'twilio'
    base_url = 'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'
    site_url = 'https://www.twilio.com/'
    path_to_errors = 'message',

    _required = {
        'allOf': [
            {
                'anyOf': [
                    {
                        'anyOf': [
                            {
                                'required':[
                                    'from'
                                ]
                            },
                            {
                                'required': [
                                    'from_'
                                ]
                            }
                        ]
                    },
                    {
                        'required': [
                            'messaging_service_id'
                        ]
                    }
                ],
                'error_anyOf': "Either 'from' or 'messaging_service_id' are required"
            },
            {
                'anyOf': [
                    {
                        'required': [
                            'message'
                        ]
                    },
                    {
                        'required': [
                            'media_url'
                        ]
                    }
                ],
                'error_anyOf': "Either 'message' or 'media_url' are required"
            },
            {
                'required': [
                    'to',
                    'account_sid',
                    'auth_token'
                ]
            }
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'The text body of the message. Up to 1,600 characters long.',
                'maxLength': 1_600
            },
            'account_sid': {
                'type': 'string',
                'title': 'The unique id of the Account that sent this message.'
            },
            'auth_token': {
                'type': 'string',
                'title': "The user's auth token"
            },
            'to': {
                'type': 'string',
                'title': 'The recipient of the message, in E.164 format'
                # todo add a custom formatter for this
            },
            'from': {
                'type': 'string',
                'title': 'Twilio phone number or the alphanumeric sender ID used'
            },
            'from_': {
                'type': 'string',
                'title': 'Twilio phone number or the alphanumeric sender ID used',
                'duplicate': True
            },
            'messaging_service_id': {
                'type': 'string',
                'title': 'The unique id of the Messaging Service used with the message'
            },
            'media_url': {
                'type': 'string',
                'title': 'The URL of the media you wish to send out with the message'
            },
            'status_callback': {
                'type': 'string',
                'title': 'A URL where Twilio will POST each time your message status changes'
            },
            'application_sid': {
                'type': 'string',
                'title': 'Twilio will POST MessageSid as well as MessageStatus=sent or MessageStatus=failed to the URL '
                         'in the MessageStatusCallback property of this Application'
            },
            'max_price': {
                'type': 'number',
                'title': 'The total maximum price up to the fourth decimal (0.0001) in US dollars acceptable for '
                         'the message to be delivered'
            },
            'provide_feedback': {
                'type': 'boolean',
                'title': 'Set this value to true if you are sending messages that have a trackable user action and '
                         'you intend to confirm delivery of the message using the Message Feedback API'
            },
            'validity_period': {
                'type': 'integer',
                'title': 'The number of seconds that the message can remain in a Twilio queue',
                'minimum': 1,
                'maximum': 14_400
            }
        }
    }

    def _prepare_data(self, data: dict) -> dict:
        if data.get('message'):
            data['body'] = data.pop('message')
        new_data = {
            'auth_token': data.pop('auth_token'),
            'account_sid': data.pop('account_sid')
        }
        for key in data:
            camel_case_key = snake_to_camel_case(key)
            new_data[camel_case_key] = data[key]
        return new_data

    def _send_notification(self, data: dict) -> Response:
        account_sid = data.pop('account_sid')
        url = self.base_url.format(account_sid)
        auth = (account_sid, data.pop('auth_token'))
        response, errors = requests.post(url, data=data, auth=auth, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
