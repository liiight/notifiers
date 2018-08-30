"""
Collection of unit and functional tests for the sendgrid library.
Online functional tests require the following env variables:
    NOTIFIERS_SENDGRID_API_KEY
    NOTIFIERS_SENDGRID_TO
The 'from' email in the online tests will be 'test@example.com'
"""
# pylint: disable=too-many-public-methods,no-self-use,redefined-outer-name
# pylint: disable=missing-docstring,invalid-name
import os
import copy
import base64
from unittest.mock import MagicMock
import pytest
from notifiers.exceptions import BadArguments
provider = 'sendgrid'


def get_basic_payload():
    """
    gets a payload with the minimum required arguments, can be updated
    with test data to test specific attributes in the payload without
    having to worry about required arguments
    """
    return {
        'api_key': '1234',
        'personalizations': [
            {
                'to': [
                    {
                        'email': 'test@example.com'
                    }
                ]
            }
        ],
        'from': {
            'email': 'test@example.com'
        },
        'subject': 'a friendly subject',
        'content': [
            {
                'type': 'text/plain',
                'value': 'my email content'
            }
        ],
    }


def get_attachment_payload():
    """Gets a payload section for attachments"""
    payload = get_basic_payload()
    payload['attachments'] = [
        {
            'content': 'my content',
            'filename': 'my file name'
        }
    ]
    return payload


class TestSendgridSchema:
    """Tests just the schema validation for SG"""

    @pytest.fixture(autouse=True)
    def patch_requests(self, monkeypatch):
        def requests_return(**kwargs):
            return MagicMock(), []
        monkeypatch.setattr('notifiers.utils.requests.post', requests_return)

    @pytest.fixture(autouse=True)
    def patch_environment(self, monkeypatch):
        monkeypatch.delenv('NOTIFIERS_SENDGRID_TO', raising=False)
        monkeypatch.delenv('NOTIFIERS_SENDGRID_API_KEY', raising=False)

    def test_sendgrid_metadata(self, provider):
        assert(provider.metadata == {
            'base_url': 'https://api.sendgrid.com/v3/mail/send',
            'site_url': 'https://sendgrid.com/docs',
            'name': 'sendgrid',
        })

    def test_basic_payload(self, provider):
        provider.notify(**get_basic_payload())

    to_payloads = [
        (
            {
                'personalizations': [
                    {
                        'to': 'someone'
                    }
                ]
            },
            "Error with sent data: 'someone' is not of type 'array'"
        ),
        (
            {
                'personalizations': [
                    {
                        'to': [
                            {
                                'name': 'someone'
                            }
                        ]
                    }
                ]
            },
            "Error with sent data: 'email' is a required property"
        ),
        (
            {
                'personalizations': [
                    {
                        'to': [
                            {
                                'email': 'test@example.com',
                                'name': 'someone'
                            },
                            {
                                'name': 'someone'
                            }
                        ]
                    }
                ]
            },
            "Error with sent data: 'email' is a required property"
        ),
        (
            {
                'personalizations': [
                    {
                        'to': [
                            {
                                'email': 'someone'
                            }
                        ]
                    }
                ]
            },
            "'someone' is not a 'email'"
        )
    ]

    @pytest.mark.parametrize('payload,error', to_payloads)
    def test_bad_personalization_to_values(self, payload, error, provider):
        full_payload = get_basic_payload()
        full_payload.update(payload)
        with pytest.raises(BadArguments, match=error):
            provider.notify(**full_payload)

    def test_personalization_multiple_to(self, provider):
        payload = get_basic_payload()
        payload.update({
            'personalizations': [
                {
                    'to': [
                        {
                            'email': 'test@example.com',
                            'name': 'testing guy'
                        },
                        {
                            'email': 'test@example.com',
                            'name': 'testing guy'
                        }
                    ]
                }
            ]
        })
        provider.notify(**payload)

    def test_personalization_simple_cc_and_bcc(self, provider):
        payload = get_basic_payload()
        payload.update({
            'personalizations': [
                {
                    'to': [
                        {
                            'email': 'test@example.com',
                            'name': 'testing guy'
                        },
                    ],
                    'cc': [
                        {
                            'email': 'test@example.com',
                            'name': 'testing guy'
                        }
                    ],
                    'bcc': [
                        {
                            'email': 'test@example.com',
                            'name': 'testing guy'
                        }
                    ]
                }
            ]
        })
        provider.notify(**payload)

    def test_personalization_headers(self, provider):
        payload = get_basic_payload()
        payload['personalizations'][0]['headers'] = {'X-Whatever': 'Value'}
        provider.notify(**payload)

    def test_personalization_subject(self, provider):
        payload = get_basic_payload()
        payload['personalizations'][0]['subject'] = 'my subject'
        provider.notify(**payload)

    def test_personalization_substitutions(self, provider):
        payload = get_basic_payload()
        payload['personalizations'][0]['substitutions'] = {'key': 'value'}
        provider.notify(**payload)

    def test_personalization_custom_args(self, provider):
        payload = get_basic_payload()
        payload['personalizations'][0]['custom_args'] = {'key': 'value'}
        provider.notify(**payload)

    def test_addtional_properties_in_personalizations(self, provider):
        payload = get_basic_payload()
        payload['personalizations'][0]['bad_data'] = 1234
        with pytest.raises(BadArguments, match="'bad_data' was unexpected"):
            provider.notify(**payload)

    def test_multiple_personalizations(self, provider):
        payload = get_basic_payload()
        payload['personalizations'].append(payload['personalizations'][0])
        provider.notify(**payload)

    def test_from_missing(self, provider):
        payload = get_basic_payload()
        del payload['from']
        with pytest.raises(BadArguments,
                           match="'from' is a required property"):
            provider.notify(**payload)

    def test_from_email_missing(self, provider):
        payload = get_basic_payload()
        del payload['from']['email']
        with pytest.raises(BadArguments,
                           match="'email' is a required property"):
            provider.notify(**payload)

    def test_from_name(self, provider):
        payload = get_basic_payload()
        payload['from']['name'] = 'bill'
        provider.notify(**payload)

    def test_from_additional_properties(self, provider):
        payload = get_basic_payload()
        payload['from']['bad_data'] = 1234
        with pytest.raises(BadArguments, match="'bad_data' was unexpected"):
            provider.notify(**payload)

    def test_reply_to_email_missing(self, provider):
        payload = get_basic_payload()
        payload['reply_to'] = {}
        with pytest.raises(BadArguments,
                           match="'email' is a required property"):
            provider.notify(**payload)

    def test_email_name(self, provider):
        payload = get_basic_payload()
        payload['reply_to'] = {'name': 'bill', 'email': 'test@example.com'}
        provider.notify(**payload)

    def test_reply_to_additional_properties(self, provider):
        payload = get_basic_payload()
        payload['reply_to'] = {'bad_data': 1234}
        with pytest.raises(BadArguments, match="'bad_data' was unexpected"):
            provider.notify(**payload)

    def test_subject_missing(self, provider):
        payload = get_basic_payload()
        del payload['subject']
        with pytest.raises(BadArguments,
                           match="'subject' is a required property"):
            provider.notify(**payload)

    def test_empty_subject(self, provider):
        payload = get_basic_payload()
        payload['subject'] = ''
        with pytest.raises(BadArguments, match="'' is too short"):
            provider.notify(**payload)

    def test_no_content(self, provider):
        payload = get_basic_payload()
        del payload['content']
        with pytest.raises(BadArguments,
                           match="'content' is a required property"):
            provider.notify(**payload)

    def test_missing_mime_type(self, provider):
        payload = get_basic_payload()
        del payload['content'][0]['type']
        with pytest.raises(BadArguments,
                           match="'type' is a required property"):
            provider.notify(**payload)

    def test_missing_content_value(self, provider):
        payload = get_basic_payload()
        del payload['content'][0]['value']
        with pytest.raises(BadArguments,
                           match="'value' is a required property"):
            provider.notify(**payload)

    def test_empty_mime_type(self, provider):
        payload = get_basic_payload()
        payload['content'][0]['type'] = ''
        with pytest.raises(BadArguments, match="'' is too short"):
            provider.notify(**payload)

    def test_empty_content_value(self, provider):
        payload = get_basic_payload()
        payload['content'][0]['value'] = ''
        with pytest.raises(BadArguments, match="'' is too short"):
            provider.notify(**payload)

    def test_basic_attachment_payload(self, provider):
        payload = get_attachment_payload()
        provider.notify(**payload)

    def test_attachment_content_missing(self, provider):
        payload = get_attachment_payload()
        del payload['attachments'][0]['content']
        with pytest.raises(BadArguments,
                           match="'content' is a required property"):
            provider.notify(**payload)

    def test_attachment_filename_missing(self, provider):
        payload = get_attachment_payload()
        del payload['attachments'][0]['filename']
        with pytest.raises(BadArguments,
                           match="'filename' is a required property"):
            provider.notify(**payload)

    def test_empty_attachment_content(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['content'] = ''
        with pytest.raises(BadArguments, match="'' is too short"):
            provider.notify(**payload)

    def test_empty_attachment_filename(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['filename'] = ''
        with pytest.raises(BadArguments, match="'' is too short"):
            provider.notify(**payload)

    def test_attachment_extra_properties(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['bad_data'] = 1234
        with pytest.raises(BadArguments, match="'bad_data' was unexpected"):
            provider.notify(**payload)

    def test_attachment_disposition_inline(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['disposition'] = 'inline'
        provider.notify(**payload)

    def test_attachment_disposition_attachment(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['disposition'] = 'attachment'
        provider.notify(**payload)

    def test_attachment_bad_disposition(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['disposition'] = 'bad_data'
        with pytest.raises(BadArguments, match="'bad_data' is not one of"):
            provider.notify(**payload)

    def test_attachment_content_id(self, provider):
        payload = get_attachment_payload()
        payload['attachments'][0]['content_id'] = 'string'
        provider.notify(**payload)

    def test_template_id(self, provider):
        payload = get_basic_payload()
        payload['template_id'] = 'string'
        provider.notify(**payload)

    def test_sections(self, provider):
        payload = get_basic_payload()
        payload['sections'] = {'key': 'value', 'key2': 'value'}
        provider.notify(**payload)

    def test_headers(self, provider):
        payload = get_basic_payload()
        payload['headers'] = {'key': 'value', 'key2': 'value'}
        provider.notify(**payload)

    def test_categories(self, provider):
        payload = get_basic_payload()
        payload['categories'] = ['a', 'b', 'c']
        provider.notify(**payload)

    def test_non_unique_categories(self, provider):
        payload = get_basic_payload()
        payload['categories'] = ['a', 'a', 'a']
        with pytest.raises(BadArguments, match="has non-unique elements"):
            provider.notify(**payload)

    def test_custom_args(self, provider):
        payload = get_basic_payload()
        payload['custom_args'] = {'key': 'value'}
        provider.notify(**payload)

    def test_send_at_invalid_timestamp(self, provider):
        payload = get_basic_payload()
        payload['send_at'] = 9999999999999999
        with pytest.raises(BadArguments,
                           match=" 9999999999999999 is not a 'timestamp'"):
            provider.notify(**payload)

    def test_send_at_valid(self, provider):
        payload = get_basic_payload()
        payload['send_at'] = 1534297539
        provider.notify(**payload)

    def test_batch_id(self, provider):
        payload = get_basic_payload()
        payload['batch_id'] = 'batch id'
        provider.notify(**payload)

    def test_asm(self, provider):
        payload = get_basic_payload()
        payload['asm'] = {
            'group_id': 1234,
            'groups_to_display': [1, 2, 3]
        }
        provider.notify(**payload)

    def test_asm_no_group_id(self, provider):
        payload = get_basic_payload()
        payload['asm'] = {}
        with pytest.raises(BadArguments,
                           match="'group_id' is a required property"):
            provider.notify(**payload)

    def test_asm_additional_properties(self, provider):
        payload = get_basic_payload()
        payload['asm'] = {
            'group_id': 1234,
            'bad_data': 1
        }
        with pytest.raises(BadArguments, match="'bad_data' was unexpected"):
            provider.notify(**payload)

    def test_ip_pool_name(self, provider):
        payload = get_basic_payload()
        payload['ip_pool_name'] = 'asdf'
        provider.notify(**payload)

    def test_mail_settings(self, provider):
        payload = get_basic_payload()
        payload['mail_settings'] = {
            'bcc': {
                'enable': True,
                'email': 'someone@example.com'
            },
            'bypass_list_management': {
                'enable': True,
            },
            'footer': {
                'enable': True,
                'text': 'some text',
                'html': '<h1>some html</h1>'
            },
            'sandbox_mode': True,
            'spam_check': {
                'enable': True,
                'threshold': 10,
                'post_to_url': 'http://foo.com'
            }
        }

        expected_payload = copy.deepcopy(payload)
        del expected_payload['api_key']
        expected_payload['mail_settings']['sandbox_mode'] = {
            'enable': True
        }
        assert provider.notify(**payload).data == expected_payload

    def test_tracking_settings(self, provider):
        payload = get_basic_payload()
        payload['tracking_settings'] = {
            'click_tracking': {
                'enable': True,
                'enable_text': True
            },
            'subscription_tracking': {
                'enable': True,
                'text': 'asdf',
                'html': '<h1>asdf</h1>',
                'substitution_tag': '[tag]'
            },
            'ganalytics': {
                'enable': True,
                'utm_source': 'something',
                'utm_medium': 'something',
                'utm_term': 'something',
                'utm_content': 'something',
                'utm_campaign': 'something'
            }
        }
        provider.notify(**payload)

    def test_from_(self, provider):
        payload = get_basic_payload()
        payload['from_'] = payload.pop('from')
        expected_payload = get_basic_payload()
        del expected_payload['api_key']
        assert provider.notify(**payload).data == expected_payload

    def test_message(self, provider):
        payload = get_basic_payload()
        payload['message'] = payload['content'][0]['value']
        del payload['content']
        expected_payload = get_basic_payload()
        del expected_payload['api_key']
        assert provider.notify(**payload).data == expected_payload

    def test_to(self, provider):
        payload = get_basic_payload()
        payload['to'] = payload['personalizations'][0]['to'][0]['email']
        del payload['personalizations']
        expected_payload = get_basic_payload()
        del expected_payload['api_key']
        assert provider.notify(**payload).data == expected_payload

    def test_to_and_personalizations(self, provider):
        payload = get_basic_payload()
        payload['to'] = 'test@example.com'
        expected_payload = copy.deepcopy(payload)
        del expected_payload['to']
        expected_payload['personalizations'].append(
            {
                'to': [
                    {
                        'email': 'test@example.com'
                    }
                ]
            }
        )
        del expected_payload['api_key']
        assert provider.notify(**payload).data == expected_payload

    def test_bare_from(self, provider):
        payload = get_basic_payload()
        payload['from'] = 'test@example.com'
        expected_payload = get_basic_payload()
        del expected_payload['api_key']
        assert provider.notify(**payload).data == expected_payload


def get_online_basic_payload():
    """
    Gets a basic payload with the live variables deleted, so that
    they can only be set on the command line
    """
    payload = get_basic_payload()
    # delete this so that the 'to' from the environment gets read in instead
    del payload['personalizations']
    del payload['api_key']
    return payload


class TestSendgridOnline:

    @pytest.mark.online
    def test_basic(self, provider):
        payload = get_online_basic_payload()
        provider.notify(**payload, raise_on_errors=True)

    @pytest.mark.online
    def test_full_payload(self, provider):
        # this tests all the payload options that can be used realistically
        # on the free tier
        payload = get_online_basic_payload()
        # make sure the personalized email gets inboxed
        payload['personalizations'] = [
            {
                'to': [
                    {
                        'email': os.environ.get('NOTIFIERS_SENDGRID_TO')
                    }
                ]
            }
        ]

        payload['personalizations'][0]['substitutions'] = {
            '{{name}}': 'Kenobi',
            '{{person}}': '{{person_section}}'
        }

        payload['sections'] = {
            '{{person_section}}': 'General {{name}}!'
        }

        payload['content'].append(
            {
                'type': 'text/html',
                'value': '<p> hello there, {{person}} {{tracking_pixel}} </p>'
            }
        )
        payload['reply_to'] = {
            'email': 'e@m.ail',
            'name': 'a reply to person'
        }
        payload['attachments'] = [
            {
                'content': base64.b64encode(b'a test attachment').decode('utf-8'),
                'type': 'text/plain',
                'filename': 'file.txt',
                'disposition': 'attachment',
            },
            {
                'content': base64.b64encode(b'an inline test attachment').decode('utf-8'),
                'type': 'text/plain',
                'filename': 'file2.txt',
                'disposition': 'inline',
                'content_id': 'test'
            }
        ]

        payload['headers'] = {
            'X-NOTIFIERS-TEST': 'notifiers test'
        }

        payload['categories'] = [
            'notifiers test'
        ]

        payload['custom_args'] = {
            'notifiers': 'test'
        }

        payload['mail_settings'] = {
            'bcc': {
                'enable': True,
                'email': os.environ.get('NOTIFIERS_SENDGRID_TO')
            },
            'footer': {
                'enable': True,
                'text': 'text footer',
                'html': '<h1> html footer </h1>'
            }
        }

        payload['tracking_settings'] = {
            'click_tracking': {
                'enable': True,
                'enable_text': True
            },
            'open_tracking': {
                'enable': True,
                'substitution_tag': '{{tracking_pixel}}'
            },
            'subscription_tracking': {
                'enable': True,
                'html': '<a href=https://www.google.com> Test Link </a>'
            }
        }

        provider.notify(**payload, raise_on_errors=True)
