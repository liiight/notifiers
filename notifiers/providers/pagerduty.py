from ..core import Provider, Response
from ..utils import requests


class PagerDuty(Provider):
    """Send PagerDuty Events"""
    name = 'pagerduty'
    base_url = 'https://events.pagerduty.com/v2/enqueue'
    site_url = 'https://v2.developer.pagerduty.com/'
    path_to_errors = 'errors',

    __payload_attributes = [
        'message',
        'source',
        'severity',
        'timestamp',
        'component',
        'group',
        'class',
        'custom_details'
    ]

    __images = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'src': {
                    'type': 'string',
                    'title': 'The source of the image being attached to the incident. '
                             'This image must be served via HTTPS.'
                },
                'href': {
                    'type': 'string',
                    'title': 'Optional URL; makes the image a clickable link'
                },
                'alt': {
                    'type': 'string',
                    'title': 'Optional alternative text for the image'
                }
            },
            'required': [
                'src'
            ],
            'additionalProperties': False
        }
    }

    __links = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'href': {
                    'type': 'string',
                    'title': 'URL of the link to be attached'
                },
                'text': {
                    'type': 'string',
                    'title': "Plain text that describes the purpose of the link, and can be used as the link's text"
                }
            },
            'required': [
                'href',
                'text'
            ],
            'additionalProperties': False
        }
    }

    _required = {
        'required': [
            'routing_key',
            'event_action',
            'source',
            'severity',
            'message'
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'A brief text summary of the event, used to generate the summaries/titles of any '
                         'associated alerts'
            },
            'routing_key': {
                'type': 'string',
                'title': 'The GUID of one of your Events API V2 integrations. This is the "Integration Key" listed on'
                         ' the Events API V2 integration\'s detail page'
            },
            'event_action': {
                'type': 'string',
                'enum': [
                    'trigger',
                    'acknowledge',
                    'resolve'
                ],
                'title': 'The type of event'
            },
            'dedup_key': {
                'type': 'string',
                'title': 'Deduplication key for correlating triggers and resolves',
                'maxLength': 255
            },
            'source': {
                'type': 'string',
                'title': 'The unique location of the affected system, preferably a hostname or FQDN'
            },
            'severity': {
                'type': 'string',
                'enum': [
                    'critical',
                    'error',
                    'warning',
                    'info'
                ],
                'title': 'The perceived severity of the status the event is describing with respect to the '
                         'affected system'
            },
            'timestamp': {
                # todo create a iso8601 format
                'type': 'string',
                'title': 'The time at which the emitting tool detected or generated the event in ISO 8601',
            },
            'component': {
                'type': 'string',
                'title': 'Component of the source machine that is responsible for the event'
            },
            'group': {
                'type': 'string',
                'title': 'Logical grouping of components of a service'
            },
            'class': {
                'type': 'string',
                'title': 'The class/type of the event'
            },
            'custom_details': {
                'type': 'object',
                'title': 'Additional details about the event and affected system'
            },
            'images': __images,
            'links': __links
        }
    }

    def _prepare_data(self, data: dict) -> dict:
        payload = {attribute: data.pop(attribute) for attribute in self.__payload_attributes if data.get(attribute)}
        payload['summary'] = payload.pop('message')
        data['payload'] = payload
        return data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url
        response, errors = requests.post(url, json=data, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
