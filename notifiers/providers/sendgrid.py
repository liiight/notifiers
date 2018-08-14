from ..core import Provider, Response
from ..utils import requests


class SendGrid(Provider):
    """Send emails via SendGrid"""
    base_url = 'https://api.sendgrid.com/v3/mail/send'
    site_url = 'https://sendgrid.com/docs'
    name = 'sendgrid'

    _required = {
        'allOf': [
            {
                'required': [
                    'subject',
                ]
            },
            {
                'anyOf': [
                    {
                        'required': [
                            'to'
                        ]
                    },
                    {
                        'required': [
                            'personalizations'
                        ]
                    }
                ]
            },
            {
                'anyOf': [
                    {
                        'required': [
                            'from'
                        ]
                    },
                    {
                        'required': [
                            'from_'
                        ]
                    }
                ],
            },
            {
                'anyOf': [
                    {
                        'required': [
                            'content'
                        ]
                    },
                    {
                        'required': [
                            'message'
                        ]
                    }
                ]
            }
        ],
    }

    __recipient_array = {
        'type': 'array',
        'title': 'A list of recipients',
        'minItems': 1,
        'maxItems': 1000,
        'uniqueItems': False,
        'items': {
            'type': 'object',
            'required': ['email'],
            'properties': {
                'email': {
                    'type': 'string',
                    'title': 'Email address of recipient',
                    'format': 'email'
                },
                'name': {
                    'type': 'string',
                    'title': 'Name of recipient'
                }
            }
        }
    }

    __from = {
        'oneOf': [
            {
                'type': 'object',
                'title': 'The from address of the email',
                'additionalProperties': False,
                'required': ['email'],
                'properties': {
                    'email': {
                        'type': 'string',
                        'title': 'The email address'
                    },
                    'name': {
                        'type': 'string',
                        'title': 'The name associated with the email address'
                    }
                }
            },
            {
                'type': 'string',
                'title': 'the email address to set in the "from" headers',
                'format': 'email'
            }
        ]
    }

    _schema = {
        'type': 'object',
        'properties': {
            'to': {
                'type': 'string',
                'title': 'The destination address of the email, will' +
                         ' be appended to the personalizations',
                'format': 'email'
            },
            'api_key': {
                'type': 'string',
                'title': 'API key for authorization'
            },
            'personalizations': {
                'type': 'array',
                'title': 'An array of messages and their metadata',
                'items': {
                    'additionalProperties': False,
                    'type': 'object',
                    'required': ['to'],
                    'properties': {
                        'to': __recipient_array,
                        'cc': __recipient_array,
                        'bcc': __recipient_array,
                        'subject': {
                            'minLength': 1,
                            'type': 'string',
                            'title': 'Subject of the personalized message'
                        },
                        'headers': {
                            'type': 'object',
                            'title': 'A collection of key/value pairs ' +
                                     'indicating headers to be overridden ' +
                                     'in this email'
                        },
                        'substitutions': {
                            'type': 'object',
                            'title': 'A collection of key/value pairs that will ' +
                                     'be applied to the text and html parts of the email',
                            'maxProperties': 10000
                        },
                        'custom_args': {
                            'type': 'object',
                            'title': 'Values that are specific to this ' +
                                     'personalization that will be carried' +
                                     ' along with the email and its activity data',
                            'maxProperties': 10000
                        },
                        'send_at': {
                            'type': 'integer',
                            'title': 'A unix timestamp allowing you to ' +
                                     'specify when you want your email ' +
                                     'to be delivered',
                        }

                    }
                }
            },
            'message': {
                'type': 'string',
                'title': 'Plain text message content'
            },
            'from': __from,
            'from_': __from,
            'reply_to': {
                'type': 'object',
                'title': 'The "reply to" address of the email',
                'additionalProperties': False,
                'required': ['email'],
                'properties': {
                    'email': {
                        'type': 'string',
                        'title': 'The email address',
                        'format': 'email'
                    },
                    'name': {
                        'type': 'string',
                        'title': 'The name associated with the email address'
                    }
                }
            },
            'subject': {
                'type': 'string',
                'title': 'The global subject of the message',
                'minLength': 1
            },
            'content': {
                'type': 'array',
                'title': 'An array in which you may specify the content' +
                         ' of your email by mime type',
                'items': {
                    'additionalProperties': False,
                    'required': ['type', 'value'],
                    'properties': {
                        'type': {
                            'type': 'string',
                            'minLength': 1,
                            'title': 'The mime type of this message part' +
                                     ' e.g "text/html"'
                        },
                        'value': {
                            'type': 'string',
                            'minLength': 1,
                            'title': 'The actual content of the specified' +
                                     ' mime type'
                        }
                    }
                }
            },
            'attachments': {
                'type': 'array',
                'title': 'An array of attachments for your email',
                'items': {
                    'additionalProperties': False,
                    'required': ['content', 'filename'],
                    'properties': {
                        'content': {
                            'type': 'string',
                            'title': 'The base64 encoded content of the' +
                                     ' attachment',
                            'minLength': 1,
                        },
                        'type': {
                            'type': 'string',
                            'title': 'The mime type of the attachment',
                            'minLength': 1
                        },
                        'filename': {
                            'type': 'string',
                            'title': 'The filename of the attachment',
                            'minLength': 1
                        },
                        'disposition': {
                            'type': 'string',
                            'default': 'attachment',
                            'enum': [
                                'inline',
                                'attachment'
                            ]
                        },
                        'content_id': {
                            'type': 'string',
                            'title': 'the content ID for the attachment' +
                                     ', used when disposition is ' +
                                     '"inline"',
                        }
                    }
                }
            },
            'template_id': {
                'type': 'string',
                'title': 'The ID of the template you would like to use'
            },
            'sections': {
                'type': 'object',
                'title': 'An object of key/value pairs that define ' +
                         'block sections to be used for substitutions'
            },
            'headers': {
                'type': 'object',
                'title': 'A collection of key/value pairs ' +
                         'indicating headers to be overridden ' +
                         'in this email'
            },
            'categories': {
                'type': 'array',
                'title': 'An array of category names for this message',
                'uniqueItems': True,
                'maxItems': 10,
                'items': {
                    'type': 'string',
                    'maxLength': 255
                }
            },
            'custom_args': {
                'type': 'object',
                'title': 'Values that are specific to the entire send ' +
                         'that will be carried along with the email and ' +
                         'its activity data'
            },
            'send_at': {
                'type': 'integer',
                'title': 'A unix timestamp allowing you to specify when ' +
                         'you want your email to be delivered'
            },
            'batch_id': {
                'type': 'string',
                'title': 'This ID represents a batch of emails to be sent at the same time.'
            },
            'asm': {
                'type': 'object',
                'title': 'An object allowing you to specify how to ' +
                         'handle unsubscribes.',
                'additionalProperties': False,
                'required': ['group_id'],
                'properties': {
                    'group_id': {
                        'type': 'integer',
                        'title': 'The unsubscribe group to associate with ' +
                                 'this email'
                    },
                    'groups_to_display': {
                        'type': 'array',
                        'title': 'An array containing the unsubscribe ' +
                                 'groups that you would like to be' +
                                 ' displayed on the unsubscribe preferences' +
                                 ' page.',
                        'maxItems': 25,
                        'items': {
                            'type': 'integer'
                        }
                    }
                }
            },
            'ip_pool_name': {
                'type': 'string',
                'title': 'The IP Pool that you would like to send this ' +
                         'email from.',
                'minLength': 2,
                'maxLength': 64
            },
            'mail_settings': {
                'type': 'object',
                'title': 'A collection of different mail settings that you ' +
                         'can use to specify how you would like this email ' +
                         'to be handled.',
                'additionalProperties': False,
                'properties': {
                    'bcc': {
                        'type': 'object',
                        'title': 'This allows you to have a blind carbon ' +
                                 'copy automatically sent to the specified ' +
                                 'email address for every email that is sent.',
                        'additionalProperties': False,
                        'properties': {
                            'email': {
                                'format': 'email',
                                'type': 'string',
                                'title': 'The email address that you would ' +
                                         'like to receive the BCC',
                            },
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is ' +
                                         'enabled.'
                            }
                        }
                    },
                    'bypass_list_management': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'Allows you to bypass all unsubscribe ' +
                                 'groups and suppressions to ensure that ' +
                                 'the email is delivered to every single ' +
                                 'recipient.',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled.'
                            }
                        }
                    },
                    'footer': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'The default footer that you would like ' +
                                 'included on every email.',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled.'
                            },
                            'text': {
                                'type': 'string',
                                'title': 'The plain text content of your ' +
                                         'footer.'
                            },
                            'html': {
                                'type': 'string',
                                'title': 'The HTML content of your footer'
                            }
                        }
                    },
                    'sandbox_mode': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'This allows you to send a test email to ' +
                                 'ensure that your request body is valid ' +
                                 'and formatted correctly.',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled'
                            }
                        }
                    },
                    'spam_check': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'This allows you to test the content ' +
                                 'of your email for spam.',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled'
                            },
                            'threshold': {
                                'type': 'integer',
                                'minimum': 1,
                                'maximum': 10,
                                'title': 'The threshold used to determine ' +
                                         'if your content qualifies as spam ' +
                                         'on a scale from 1 to 10, with 10 ' +
                                         'being most strict, or most likely ' +
                                         'to be considered as spam.'
                            },
                            'post_to_url': {
                                'type': 'string',
                                'title': 'An Inbound Parse URL that you ' +
                                         'would like a copy of your email ' +
                                         'along with the spam report to be ' +
                                         'sent to.'
                            }
                        }
                    }
                }
            },
            'tracking_settings': {
                'type': 'object',
                'additionalProperties': False,
                'title': 'Settings to determine how you would like to ' +
                         'track the metrics of how your recipients interact '+
                         'with your email.',
                'properties': {
                    'click_tracking': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'Allows you to track whether a recipient ' +
                                 'clicked a link in your email.',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled'
                            },
                            'enable_text': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting should ' +
                                         'be included in the text/plain ' +
                                         'portion of your email.'
                            }
                        }
                    },
                    'open_tracking': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'Allows you to track whether the email was ' +
                                 'opened or not',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled'
                            },
                            'substitution_tag': {
                                'type': 'string',
                                'title': 'Allows you to specify a ' +
                                         'substitution tag that you can ' +
                                         'insert in the body of your ' +
                                         'email at a location that you ' +
                                         'desire. This tag will be ' +
                                         'replaced by the open tracking '+
                                         'pixel.'
                            }
                        }
                    },
                    'subscription_tracking': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'Allows you to insert a subscription ' +
                                 'management link at the bottom of the text' +
                                 ' and html bodies of your email. If you' +
                                 ' would like to specify the location of ' +
                                 'the link within your email, you may use ' +
                                 'the substitution_tag.',
                        'properties': {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled'
                            },
                            'text': {
                                'type': 'string',
                                'title': 'Text to be appended to the email, ' +
                                         'with the subscription tracking ' +
                                         'link. You may control where the ' +
                                         'link is by using the tag <% %>'
                            },
                            'html': {
                                'type': 'string',
                                'title': 'HTML to be appended to the email, ' +
                                         'with the subscription tracking ' +
                                         'link. You may control where the ' +
                                         'link is by using the tag <% %>'
                            },
                            'substitution_tag': {
                                'type': 'string',
                                'title': 'A tag that will be replaced with the ' +
                                         'unsubscribe URL. for example: ' +
                                         '[unsubscribe_url]. If this ' +
                                         'parameter is used, it will override' +
                                         ' both the text and html parameters.' +
                                         ' The URL of the link will be placed' +
                                         ' at the substitution tag’s location' +
                                         ', with no additional formatting.'
                            }
                        }
                    },
                    'ganalytics': {
                        'type': 'object',
                        'additionalProperties': False,
                        'title': 'Allows you to insert a subscription ' +
                                 'management link at the bottom of the text' +
                                 ' and html bodies of your email. If you ' +
                                 'would like to specify the location of the' +
                                 ' link within your email, you may use the ' +
                                 'substitution_tag.',
                        'properties' : {
                            'enable': {
                                'type': 'boolean',
                                'title': 'Indicates if this setting is enabled'
                            },
                            'utm_source': {
                                'type': 'string',
                                'title': 'Name of the referrer source.' +
                                         ' (e.g. Google, SomeDomain.com,' +
                                         ' or Marketing Email)'
                            },
                            'utm_medium': {
                                'type': 'string',
                                'title': 'Name of the marketing medium. ' +
                                         '(e.g. Email)'
                            },
                            'utm_term': {
                                'type': 'string',
                                'title': 'Used to identify any paid keywords.'
                            },
                            'utm_content': {
                                'type': 'string',
                                'title': 'Used to differentiate your ' +
                                         'campaign from advertisements.'
                            },
                            'utm_campaign': {
                                'type': 'string',
                                'title': 'The name of the campaign'
                            }
                        }
                    }
                }
            }
        },
        'additionalProperties': False
    }

    def _prepare_data(self, data: dict) -> dict:
        if data.get('from_'):
            data['from'] = data.pop('from_')

        # supporting a bare string 'from', this simplifies
        # the API and allows us to use the CLI
        if isinstance(data['from'], str):
            data['from'] = {
                'email': data.pop('from')
            }

        if data.get('message'):
            content = [
                {
                    'type': 'text/plain',
                    'value': data.pop('message')
                }
            ]
            data['content'] = content

        # inserting support for a 'to' argument, since sendgrid is a little
        # complicated about setting that
        if data.get('to'):

            if not data.get('personalizations'):
                data['personalizations'] = []

            data['personalizations'].append(
                {
                    'to': [
                        {
                            'email': data.pop('to')
                        }
                    ]
                }
            )


        return data

    def _send_notification(self, data: dict) -> Response:
        headers = {
            'Authorization': f'Bearer {data["api_key"]}',
            'Content-Type': 'application/json'
        }
        del data['api_key']
        response, errors = requests.post(url=self.base_url,
                                         json=data,
                                         headers=headers
                                        )
        return self.create_response(data, response, errors)
