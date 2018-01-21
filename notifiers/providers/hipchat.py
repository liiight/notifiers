import copy

from ..core import Provider, Response, ProviderResource
from ..utils import requests
from ..exceptions import ResourceError


class HipChatProxy:
    """Shared attributed between resources and :class:`HipChatResourceProxy`"""
    base_url = 'https://{group}.hipchat.com'
    name = 'hipchat'
    path_to_errors = 'error', 'message'
    users_url = '/v2/user'
    rooms_url = '/v2/room'

    def _get_headers(self, token: str) -> dict:
        """
        Builds hipchat requests header bases on the token provided

        :param token: App token
        :return: Authentication header dict
        """
        return {'Authorization': f'Bearer {token}'}


class HipChatResourceProxy(HipChatProxy):
    """Common resources attributes that should not override :class:`HipChat` attributes"""
    _required = {
        'allOf': [
            {
                'required': [
                    'token'
                ]
            },
            {
                'oneOf': [
                    {'required': ['group']},
                    {'required': ['team_server']}
                ],
                'error_oneOf': "Only one 'group' or 'team_server' is allowed"
            }
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'token': {
                'type': 'string',
                'title': 'User token'
            },
            'start': {
                'type': 'integer',
                'title': 'Start index'
            },
            'max_results': {
                'type': 'integer',
                'title': 'Max results in reply'
            },
            'group': {
                'type': 'string',
                'title': 'Hipchat group name',
            },
            'team_server': {
                'type': 'string',
                'title': 'Hipchat team server'
            }
        },
        'additionalProperties': False
    }

    def _get_resources(self, endpoint: str, data: dict) -> tuple:
        url = self.base_url.format(group=data['group']) if data.get('group') else data['team_server']
        url += endpoint
        headers = self._get_headers(data['token'])
        params = {}
        if data.get('start'):
            params['start-index'] = data['start']
        if data.get('max_results'):
            params['max-results'] = data['max_results']
        if data.get('private'):
            params['include-private'] = data['private']
        if data.get('archived'):
            params['include-archived'] = data['archived']
        if data.get('guests'):
            params['include-guests'] = data['guests']
        if data.get('deleted'):
            params['include-deleted'] = data['deleted']
        return requests.get(url, headers=headers, params=params, path_to_errors=self.path_to_errors)


class HipChatUsers(HipChatResourceProxy, ProviderResource):
    """Return a list of HipChat users"""
    resource_name = 'users'

    @property
    def _schema(self):
        user_schema = {
            'guests': {
                'type': 'boolean',
                'title': 'Include active guest users in response. Otherwise, no guest users will be included'
            },
            'deleted': {
                'type': 'boolean',
                'title': 'Include deleted users'
            }
        }
        schema = copy.deepcopy(super()._schema)
        schema['properties'].update(user_schema)
        return schema

    def _get_resource(self, data: dict):
        response, errors = self._get_resources(self.users_url, data)
        if errors:
            raise ResourceError(errors=errors,
                                resource=self.resource_name,
                                provider=self.name,
                                data=data,
                                response=response)
        return response.json()


class HipChatRooms(HipChatResourceProxy, ProviderResource):
    """Return a list of HipChat rooms"""
    resource_name = 'rooms'

    @property
    def _schema(self):
        user_schema = {
            'private': {
                'type': 'boolean',
                'title': 'Include private rooms'
            },
            'archived': {
                'type': 'boolean',
                'title': 'Include archive rooms'
            }
        }
        schema = copy.deepcopy(super()._schema)
        schema['properties'].update(user_schema)
        return schema

    def _get_resource(self, data: dict):
        response, errors = self._get_resources(self.rooms_url, data)
        if errors:
            raise ResourceError(errors=errors,
                                resource=self.resource_name,
                                provider=self.name,
                                data=data,
                                response=response)
        return response.json()


class HipChat(HipChatProxy, Provider):
    """Send HipChat notifications"""

    room_notification = '/{room}/notification'
    user_message = '/{user}/message'
    site_url = 'https://www.hipchat.com/docs/apiv2'

    __icon = {
        'oneOf': [
            {
                'type': 'string',
                'title': 'The url where the icon is'
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

    _required = {
        'allOf': [
            {'required': ['message', 'id', 'token']},
            {'oneOf': [
                {'required': ['room']},
                {'required': ['user']}
            ],
                'error_oneOf': "Only one of 'room' or 'user' is allowed"},
            {'oneOf': [
                {'required': ['group']},
                {'required': ['team_server']}
            ],
                'error_oneOf': "Only one 'group' or 'team_server' is allowed"}
        ]
    }
    _schema = {
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
                'title': "The id, email address, or mention name (beginning with an '@') "
                         "of the user to send a message to."
            },
            'message': {
                'type': 'string',
                'title': 'The message body',
                'maxLength': 10_000,
                'minLength': 1
            },
            'token': {
                'type': 'string',
                'title': 'User token'
            },
            'notify': {
                'type': 'boolean',
                'title': "Whether this message should trigger a user notification (change the tab color,"
                         " play a sound, notify mobile phones, etc). Each recipient's notification preferences "
                         "are taken into account."
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
                'title': "A label to be shown in addition to the sender's name"
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
            'card': __card,
            'id': {
                'type': 'string',
                'title': 'An id that will help HipChat recognise the same card when it is sent multiple times'
            },
            'icon': __icon,
            'team_server': {
                'type': 'string',
                'title': "An alternate team server. Example: 'https://hipchat.corp-domain.com'"
            },
            'group': {
                'type': 'string',
                'title': 'HipChat group name'
            }
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        if data.get('team_server'):
            base_url = data['team_server']
        else:
            base_url = self.base_url.format(group=data.pop('group'))
        if data.get('room'):
            url = base_url + self.rooms_url + self.room_notification.format(room=data.pop('room'))
        else:
            url = base_url + self.users_url + self.user_message.format(user=data.pop('user'))
        data['url'] = url
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop('url')
        headers = self._get_headers(data.pop('token'))
        response, errors = requests.post(url, json=data, headers=headers, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)

    @property
    def resources(self) -> list:
        return [
            'rooms',
            'users'
        ]

    @property
    def users(self) -> HipChatUsers:
        return HipChatUsers()

    @property
    def rooms(self) -> HipChatRooms:
        return HipChatRooms()
