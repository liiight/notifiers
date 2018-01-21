import requests
import json

from ..core import Provider, Response, ProviderResource
from ..utils.json_schema import one_or_more, list_to_commas
from ..exceptions import ResourceError


class JoinProxy:
    """Shared resources between :class:`Join` and :class:`JoinDevices`"""
    name = 'join'
    base_url = 'https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1'

    def _join_request(self, url: str, data: dict) -> tuple:
        # Can 't use generic requests util since API doesn't always return error status
        errors = None
        try:
            response = requests.get(url, params=data)
            response.raise_for_status()
            rsp = response.json()
            if not rsp['success']:
                errors = [rsp['errorMessage']]
        except requests.RequestException as e:
            if e.response is not None:
                response = e.response
                try:
                    errors = [response.json()['errorMessage']]
                except json.decoder.JSONDecodeError:
                    errors = [response.text]
            else:
                response = None
                errors = [(str(e))]

        return response, errors


class JoinDevices(JoinProxy, ProviderResource):
    """Return a list of Join devices IDs"""
    resource_name = 'devices'
    devices_url = '/listDevices'
    _required = {
        'required': [
            'apikey'
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'apikey': {
                'type': 'string',
                'title': 'user API key'
            }
        },
        'additionalProperties': False
    }

    def _get_resource(self, data: dict):
        url = self.base_url + self.devices_url
        response, errors = self._join_request(url, data)
        if errors:
            raise ResourceError(errors=errors,
                                resource=self.resource_name,
                                provider=self.name,
                                data=data,
                                response=response)
        return response.json()['records']


class Join(JoinProxy, Provider):
    """Send Join notifications"""
    push_url = '/sendPush'
    site_url = 'https://joaoapps.com/join/api/'

    _required = {
        'dependencies': {
            'smstext': ['smsnumber'],
            'callnumber': ['smsnumber']
        },
        'anyOf': [
            {
                'dependencies': {
                    'smsnumber': ['smstext']
                }
            },
            {
                'dependencies': {
                    'smsnumber': ['mmsfile']
                }
            }
        ],
        'error_anyOf': "Must use either 'smstext' or 'mmsfile' with 'smsnumber'",
        'required': ['apikey', 'message']
    }

    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'usually used as a Tasker or EventGhost command. Can also be used with URLs and Files '
                         'to add a description for those elements'
            },
            'apikey': {
                'type': 'string',
                'title': 'user API key'
            },
            'deviceId': {
                'type': 'string',
                'title': 'The device ID or group ID of the device you want to send the message to'
            },
            'deviceIds': one_or_more({
                'type': 'string',
                'title': 'A comma separated list of device IDs you want to send the push to'
            }),
            'deviceNames': one_or_more({
                'type': 'string',
                'title': 'A comma separated list of device names you want to send the push to'
            }),
            'url': {
                'type': 'string',
                'title': ' A URL you want to open on the device. If a notification is created with this push, '
                         'this will make clicking the notification open this URL'
            },
            'clipboard': {
                'type': 'string',
                'title': 'some text you want to set on the receiving device’s clipboard'
            },
            'file': {
                'type': 'string',
                'title': 'a publicly accessible URL of a file'
            },
            'smsnumber': {
                'type': 'string',
                'title': 'phone number to send an SMS to'
            },
            'smstext': {
                'type': 'string',
                'title': 'some text to send in an SMS'
            },
            'callnumber': {
                'type': 'string',
                'title': 'number to call to'
            },
            'interruptionFilter': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 4,
                'title': 'set interruption filter mode'
            },
            'mmsfile': {
                'type': 'string',
                'title': 'publicly accessible mms file url'
            },
            'mediaVolume': {
                'type': 'integer',
                'title': 'set device media volume'
            },
            'ringVolume': {
                'type': 'string',
                'title': 'set device ring volume'
            },
            'alarmVolume': {
                'type': 'string',
                'title': 'set device alarm volume'
            },
            'wallpaper': {
                'type': 'string',
                'title': 'a publicly accessible URL of an image file'
            },
            'find': {
                'type': 'boolean',
                'title': 'set to true to make your device ring loudly'
            },
            'title': {
                'type': 'string',
                'title': 'If used, will always create a notification on the receiving device with this as the '
                         'title and text as the notification’s text'
            },
            'icon': {
                'type': 'string',
                'title': "notification's icon"
            },
            'smallicon': {
                'type': 'string',
                'title': 'Status Bar Icon'
            },
            'priority': {
                'type': 'integer',
                'title': 'control how your notification is displayed',
                'minimum': -2,
                'maximum': 2
            },
            'group': {
                'type': 'string',
                'title': 'allows you to join notifications in different groups'
            },
            'image': {
                'type': 'string',
                'title': 'Notification image'
            }
        },
        'additionalProperties': False
    }

    @property
    def defaults(self) -> dict:
        return {
            'deviceId': 'group.all'
        }

    def _prepare_data(self, data: dict) -> dict:
        if data.get('deviceIds'):
            data['deviceIds'] = list_to_commas(data['deviceIds'])
        if data.get('deviceNames'):
            data['deviceNames'] = list_to_commas(data['deviceNames'])
        data['text'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        # Can 't use generic requests util since API doesn't always return error status
        url = self.base_url + self.push_url
        response, errors = self._join_request(url, data)
        return self.create_response(data, response, errors)

    @property
    def resources(self):
        return [
            'devices'
        ]

    @property
    def devices(self) -> JoinDevices:
        return JoinDevices()
