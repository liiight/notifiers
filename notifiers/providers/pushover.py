from pathlib import Path

from requests_toolbelt import MultipartEncoder

from ..core import Provider, Response, ProviderResource
from ..exceptions import ResourceError, BadArguments
from ..utils import requests
from ..utils.json_schema import one_or_more, list_to_commas


class PushoverProxy:
    name = 'pushover'
    base_url = 'https://api.pushover.net/1/'
    path_to_errors = 'errors',


class PushoverResourceProxy:
    _required = {
        'required': [
            'token'
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'token': {
                'type': 'string',
                'title': "your application's API token"
            }
        }
    }


class PushoverSounds(PushoverProxy, PushoverResourceProxy, ProviderResource):
    resource_name = 'sounds'
    sounds_url = 'sounds.json'

    def _get_resource(self, data: dict):
        url = self.base_url + self.sounds_url
        params = {
            'token': data['token']
        }
        response, errors = requests.get(url, params=params, path_to_errors=self.path_to_errors)
        if errors:
            raise ResourceError(errors=errors,
                                resource=self.resource_name,
                                provider=self.name,
                                data=data,
                                response=response)
        return list(response.json()['sounds'].keys())


class PushoverLimits(PushoverProxy, PushoverResourceProxy, ProviderResource):
    resource_name = 'limits'
    limits_url = 'apps/limits.json'

    def _get_resource(self, data: dict):
        url = self.base_url + self.limits_url
        params = {
            'token': data['token']
        }
        response, errors = requests.get(url, params=params, path_to_errors=self.path_to_errors)
        if errors:
            raise ResourceError(errors=errors,
                                resource=self.resource_name,
                                provider=self.name,
                                data=data,
                                response=response)
        return response.json()


class Pushover(PushoverProxy, Provider):
    """Send Pushover notifications"""
    message_url = 'messages.json'
    site_url = 'https://pushover.net/'
    name = 'pushover'

    _required = {'required': ['user', 'message', 'token']}
    _schema = {
        'type': 'object',
        'properties': {
            'user': one_or_more({
                'type': 'string',
                'title': 'the user/group key (not e-mail address) of your user (or you)'
            }),
            'message': {
                'type': 'string',
                'title': 'your message'
            },
            'title': {
                'type': 'string',
                'title': "your message's title, otherwise your app's name is used"
            },
            'token': {
                'type': 'string',
                'title': "your application's API token"
            },
            'device': one_or_more({
                'type': 'string',
                'title': "your user's device name to send the message directly to that device"
            }),
            'priority': {
                'type': 'integer',
                'minimum': -2,
                'maximum': 2,
                'title': 'notification priority'
            },
            'url': {
                'type': 'string',
                'format': 'uri',
                'title': 'a supplementary URL to show with your message'
            },
            'url_title': {
                'type': 'string',
                'title': 'a title for your supplementary URL, otherwise just the URL is shown'
            },
            'sound': {
                'type': 'string',
                'title': "the name of one of the sounds supported by device clients to override the "
                         "user's default sound choice. See `sounds` resource",
            },
            'timestamp': {
                'type': 'integer',
                'minimum': 0,
                'title': "a Unix timestamp of your message's date and time to display to the user, "
                         "rather than the time your message is received by our API"
            },
            'retry': {
                'type': 'integer',
                'minimum': 30,
                'title': 'how often (in seconds) the Pushover servers will send the same notification to the '
                         'user. priority must be set to 2'
            },
            'expire': {
                'type': 'integer',
                'maximum': 86400,
                'title': 'how many seconds your notification will continue to be retried for. '
                         'priority must be set to 2'
            },
            'callback': {
                'type': 'string',
                'format': 'uri',
                'title': 'a publicly-accessible URL that our servers will send a request to when the user'
                         ' has acknowledged your notification. priority must be set to 2'
            },
            'html': {
                'type': 'boolean',
                'title': 'enable HTML formatting'
            },
            'attachment': {
                'type': 'string',
                'title': 'an image attachment to send with the message'
            }
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        data['user'] = list_to_commas(data['user'])
        if data.get('device'):
            data['device'] = list_to_commas(data['device'])
        if data.get('html') is not None:
            data['html'] = int(data['html'])
        return data

    def _validate_data_dependencies(self, data: dict):
        if data.get('attachment'):
            path = Path(data['attachment']).expanduser()
            if not path.exists():
                raise BadArguments(provider=self.name, validation_error=f"Path does not exist '{path}'")
        return data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url + self.message_url
        headers = {}
        if data.get('attachment'):
            attachment = data['attachment']
            data['attachment'] = (attachment, open(attachment, mode='rb'))
            data = MultipartEncoder(fields=data)
            headers['Content-Type'] = data.content_type
        response, errors = requests.post(url,
                                         data=data,
                                         headers=headers,
                                         path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)

    @property
    def metadata(self) -> dict:
        m = super().metadata
        m['message_url'] = self.message_url
        return m

    @property
    def resources(self) -> list:
        return [
            'sounds',
            'limits'
        ]

    @property
    def sounds(self) -> PushoverSounds:
        return PushoverSounds()

    @property
    def limits(self) -> PushoverLimits:
        return PushoverLimits()

    # todo create devices method
