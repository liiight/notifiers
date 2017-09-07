import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestSlack(object):
    """
    Slack web hook tests

    Online test rely on setting the env variable NOTIFIERS_SLACK_WEBHOOK_URL
    """

    def test_slack_metadata(self):
        p = get_notifier('slack')
        assert p.metadata == {
            'base_url': 'https://hooks.slack.com/services/',
            'provider_name': 'slack',
            'site_url': 'https://api.slack.com/incoming-webhooks'
        }

    @pytest.mark.online
    def test_sanity(self):
        p = get_notifier('slack')
        data = {'message': 'foo'}
        rsp = p.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self):
        p = get_notifier('slack')
        data = {
            'message': 'http://foo.com',
            'icon_emoji': 'poop',
            'username': 'test',
            'channel': 'test',
            'attachments': {
                'fallback': 'fallback text',
                'text': 'attach this',
                'pretext': 'pre-attach this',
                'color': 'good',
                'fields': [
                    {
                        'title': 'test_title',
                        'value': 'test_value',
                        'short': False
                    }
                ]
            }

        }
        rsp = p.notify(**data)
        rsp.raise_on_errors()
