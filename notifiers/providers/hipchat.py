import requests

from ..core import Provider, Response
from ..utils.helpers import create_response
from ..exceptions import NotifierException


class HipChat(Provider):
    base_url = 'https://{group}.hipchat.com'
    room_url = '/v2/room'
    user_url = '/v2/user'
    room_notification_url = room_url + '/{room}/notification'
    user_message_url = user_url + '/{user}/message'
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

    __required = {
        'allOf': [
            {'required': ['message', 'id', 'token']},
            {'oneOf': [
                {'required': ['room']},
                {'required': ['user']}
            ]},
            {'oneOf': [
                {'required': ['group']},
                {'required': ['team_server']}
            ]}
        ]
    }

    @property
    def schema(self) -> dict:
        schema = {
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
                'token': {
                    'type': 'string',
                    'title': 'User token'
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
                    'type': 'string',
                    'title': 'An alternate team server. Example: \'https://hipchat.corp-domain.com\''
                },
                'group': {
                    'type': 'string',
                    'title': 'HipChat group name'
                }
            },
            'additionalProperties': False
        }
        schema.update(self.__required)
        return schema

    @property
    def required(self) -> dict:
        return self.__required

    def _prepare_data(self, data: dict) -> dict:
        base_url = self.base_url.format(group=data.pop('group')) if not data.get('team_server') else data.pop(
            'team_server')
        if data.get('room'):
            base_url += self.room_notification_url.format(room=data.pop('room'))
        elif data.get('user'):
            base_url += self.user_message_url.format(user=data.pop('user'))
        data['url'] = base_url
        return data

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata['room_url'] = self.room_notification_url
        metadata['user_url'] = self.user_message_url
        return metadata

    def _get_headers(self, token: str) -> dict:
        """
        Builds hipchat requests header bases on the token provided

        :param token: App token
        :return: Authentication header dict
        """
        return {'Authorization': f'Bearer {token}'}

    def _send_notification(self, data: dict) -> Response:
        url = data.pop('url')
        headers = self._get_headers(data.pop('token'))
        response_data = {
            'provider_name': self.provider_name,
            'data': data
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            response_data['response'] = response
        except requests.RequestException as e:
            if e.response is not None:
                response_data['response'] = e.response
                response_data['errors'] = [e.response.json()['error']['message']]
            else:
                response_data['errors'] = [(str(e))]
        return create_response(**response_data)

    def _get_resources(self, resource_name: str, token: str, group: str = None, team_server: str = None,
                       **kwargs) -> dict:
        """
        Helper method to view group resources
        :param resource_name: Resource selector, `room` or `user`
        :param token: User token
        :param group: Hipchat group name. Either this or `team_server` is required
        :param team_server: Hipchat team server. Either this or `group` is required
        :param kwargs: Additional request options
        :return: Dict of resources
        """

        options = [group, team_server]
        if not any(options) or all(options):
            raise NotifierException(provider=self.provider_name,
                                    message='Must provide exactly one of \'group\' or \'team_server\'')
        url = self.base_url.format(group) if group else team_server
        url += self.room_url if resource_name == 'room' else self.user_url
        headers = self._get_headers(token)
        params = {}
        if kwargs.get('start'):
            params['start-index'] = kwargs['start']
        if kwargs.get('max_results'):
            params['max-results'] = kwargs['max_results']
        if kwargs.get('private'):
            params['include-private'] = kwargs['private']
        if kwargs.get('archived'):
            params['include-archived'] = kwargs['archived']
        if kwargs.get('guests'):
            params['include-guests'] = kwargs['guests']
        if kwargs.get('deleted'):
            params['include-deleted'] = kwargs['deleted']
        try:
            rsp = requests.get(url, headers=headers, params=params)
            rsp.raise_for_status()
            return rsp.json()
        except requests.RequestException as e:
            message = e.response.json()['error']['message']
            raise NotifierException(provider=self.provider_name, message=message)

    def users(self, token: str, group: str = None, team_server: str = None, start: int = 1, max_results: int = 100,
              guests: bool = False, deleted: bool = False) -> dict:
        """
        View all available rooms via the used Token. Requires the 'view_group' scope

        :param token: User token
        :param start: Start index
        :param max: Max results in reply. Max value is 1000
        :param group: Hipchat group name. Either this or `team_server` is required
        :param team_server: Hipchat team server. Either this or `group` is required
        :param guests: Include active guest users in response. Otherwise, no guest users will be included.
        :param deleted: Include deleted users in response
        :return: Dict of rooms
        """
        return self._get_resources('user', token, group=group, team_server=team_server, start=start,
                                   max_results=max_results, guests=guests, deleted=deleted)

    def rooms(self, token: str, group: str = None, team_server: str = None, start: int = 1, max_results: int = 100,
              private: bool = True, archived: bool = False) -> dict:
        """
        View all available rooms via the used Token. Requires the 'manage_rooms' scope

        :param token: User token
        :param start: Start index
        :param max: Max results in reply. Max value is 1000
        :param group: Hipchat group name. Either this or `team_server` is required
        :param team_server: Hipchat team server. Either this or `group` is required
        :param private: Include private rooms
        :param archived: Include archived rooms
        :return: Dict of rooms
        """
        return self._get_resources('room', token, group=group, team_server=team_server, start=start,
                                   max_results=max_results, private=private, archived=archived)
