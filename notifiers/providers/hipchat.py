import requests

from ..core import Provider, Response
from ..utils.helpers import create_response
from ..exceptions import NotifierException


class HipChat(Provider):
    base_url = 'https://{group}.hipchat.com'
    room_url = '/v2/room/{room}/notification'
    user_url = '/v2/user/{user}/message'
    site_url = 'https://www.hipchat.com/docs/apiv2'
    provider_name = 'hipchat'

    __icon = {
        'oneOf': [
            {
                'type': 'string'
            },
            {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'title': 'The url where the icon is'
                    },
                    'url@2x': {
                        'type': 'string',
                        'title': 'The url for the icon in retina'
                    }
                },
                'required': ['url'],
                'additionalProperties': False
            }
        ]
    }

    __value = {
        'type': 'object',
        'properties': {
            'url': {
                'type': 'string',
                'title': 'Url to be opened when a user clicks on the label'
            },
            'style': {
                'type': 'string',
                'enum': [
                    'lozenge-success', 'lozenge-error', 'lozenge-current', 'lozenge-complete', 'lozenge-moved',
                    'lozenge'
                ],
                'title': 'AUI Integrations for now supporting only lozenges'
            },
            'label': {
                'type': 'string',
                'title': 'The text representation of the value'
            },
            'icon': __icon
        }
    }

    __attributes = {
        'type': 'array',
        'title': 'List of attributes to show below the card',
        'items': {
            'type': 'object',
            'properties': {
                'value': __value,
                'label': {
                    'type': 'string',
                    'title': 'Attribute label',
                    'minLength': 1,
                    'maxLength': 50
                }
            },
            'required': ['label', 'value'],
            'additionalProperties': False
        }
    }

    __activity = {
        'type': 'object',
        'properties': {
            'html': {
                'type': 'string',
                'title': 'Html for the activity to show in one line a summary of the action that happened'
            },
            'icon': __icon,
        },
        'required': ['html'],
        'additionalProperties': False
    }

    __thumbnail = {
        'type': 'object',
        'properties': {
            'url': {
                'type': 'string',
                'minLength': 1,
                'maxLength': 250,
                'title': 'The thumbnail url'
            },
            'width': {
                'type': 'integer',
                'title': 'The original width of the image'
            },
            'url@2x': {
                'type': 'string',
                'minLength': 1,
                'maxLength': 250,
                'title': 'The thumbnail url in retina'
            },
            'height': {
                'type': 'integer',
                'title': 'The original height of the image'
            }
        },
        'required': ['url'],
        'additionalProperties': False
    }

    __format = {
        'type': 'string',
        'enum': [
            'text', 'html'
        ],
        'title': 'Determines how the message is treated by our server and rendered inside HipChat '
                 'applications'
    }

    __description = {
        'oneOf': [
            {
                'type': 'string'
            },
            {
                'type': 'object',
                'properties': {
                    'value': {
                        'type': 'string',
                        'minLength': 1,
                        'maxLength': 1000
                    },
                    'format': __format
                },
                'required': ['value', 'format'],
                'additionalProperties': False
            }
        ]
    }

    __card = {
        'type': 'object',
        'properties': {
            'style': {
                'type': 'string',
                'enum': [
                    'file', 'image', 'application', 'link', 'media'
                ],
                'title': 'Type of the card'
            },
            'description': __description,
            'format': {
                'type': 'string',
                'enum': [
                    'compact', 'medium'
                ],
                'title': 'Application cards can be compact (1 to 2 lines) or medium (1 to 5 lines)'
            },
            'url': {
                'type': 'string',
                'title': 'The url where the card will open'
            },
            'title': {
                'type': 'string',
                'minLength': 1,
                'maxLength': 500,
                'title': 'The title of the card'
            },
            'thumbnail': __thumbnail,
            'activity': __activity,
            'attributes': __attributes,
        },
        'required': ['style', 'title'],
        'additionalProperties': False
    }

    @property
    def schema(self):
        return {
            'type': 'object',
            'properties': {
                'room': {
                    'type': 'string',
                    'title': 'The id or url encoded name of the room',
                    'maxLength': 100,
                    'minLength': 1
                },
                'user': {
                    'type': 'string',
                    'title': 'The id, email address, or mention name (beginning with an \'@\') of the user to send a '
                             'message to.'
                },
                'message': {
                    'type': 'string',
                    'title': 'The message body',
                    'maxLength': 10_000,
                    'minLength': 1
                },
                'notify': {
                    'type': 'boolean',
                    'title': 'Whether this message should trigger a user notification (change the tab color,'
                             ' play a sound, notify mobile phones, etc). Each recipient\'s notification preferences '
                             'are taken into account.'
                },
                'message_format': {
                    'type': 'string',
                    'enum': [
                        'text', 'html'
                    ],
                    'title': 'Determines how the message is treated by our server and rendered inside HipChat '
                             'applications'
                },
                'from': {
                    'type': 'string',
                    'title': 'A label to be shown in addition to the sender\'s name'
                },
                'color': {
                    'type': 'string',
                    'enum': [
                        'yellow', 'green', 'red', 'purple', 'gray', 'random'
                    ],
                    'title': 'Background color for message'
                },
                'attach_to': {
                    'type': 'string',
                    'title': 'The message id to to attach this notification to'
                },
                'card': self.__card,
                'id': {
                    'type': 'string',
                    'title': 'An id that will help HipChat recognise the same card when it is sent multiple times'
                },
                'icon': self.__icon,
                'team_server': {
                    'type': ' string',
                    'title': 'An alternate team server'
                }
            },
            'required': ['message', 'id'],
            'oneOf': [
                {
                    'required': ['room']
                },
                {
                    'required': ['user']
                }
            ],
            'additionalProperties': False
        }
