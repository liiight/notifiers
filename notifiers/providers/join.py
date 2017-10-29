import requests

from ..core import Provider, Response
from ..utils.json_schema import one_or_more, list_to_commas
from ..utils.helpers import create_response
from ..exceptions import NotifierException


class Join(Provider):
    base_url = 'https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush'
    devices_url = 'https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices'
    site_url = 'https://joaoapps.com/join/api/'
    provider_name = 'join'

    @property
    def schema(self) -> dict:
        return {
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
                    'title': 'notification\'s icon'
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
                    'dependencies':{
                        'smsnumber': ['mmsfile']
                    }
                }
            ],
            'error_anyOf': 'Must use either \'smstext\' or \'mmsfile\' with \'smsnumber\'',
            'required': ['apikey', 'message'],
            'additionalProperties': False
        }

    @property
    def defaults(self) -> dict:
        return {
            'deviceId': 'group.all'
        }

    @property
    def metadata(self) -> dict:
        data = super().metadata
        data['devices_url'] = self.devices_url
        return data

    def _prepare_data(self, data: dict) -> dict:
        if data.get('deviceIds'):
            data['deviceIds'] = list_to_commas(data['deviceIds'])
        if data.get('deviceNames'):
            data['deviceNames'] = list_to_commas(data['deviceNames'])
        data['text'] = data.pop('message')
        return data

    def _send_notification(self, data: dict) -> Response:
        response_data = {
            'provider_name': self.provider_name,
            'data': data
        }
        try:
            response = requests.get(self.base_url, params=data)
            response.raise_for_status()
            response_data['response'] = response
            rsp = response.json()
            if not rsp['success']:
                response_data['errors'] = [rsp['errorMessage']]
        except requests.RequestException as e:
            if e.response is not None:
                response_data['response'] = e.response
                response_data['errors'] = [e.response.json()['errorMessage']]
            else:
                response_data['errors'] = [(str(e))]

        return create_response(**response_data)

    def devices(self, apikey: str) -> list:
        """
        Returns a list of devices corresponding with the api key

        :param apikey: user api key
        :return: List of devices
        """
        params = {
            'apikey': apikey
        }
        try:
            response = requests.get(self.devices_url, params=params)
            response.raise_for_status()
            rsp = response.json()
            if not rsp['success']:
                message = rsp['errorMessage']
                raise NotifierException(provider=self.provider_name, message=message)
        except requests.RequestException as e:
            message = e.response.json()['errorMessage']
            raise NotifierException(provider=self.provider_name, message=message)
        return response.json()['records']
