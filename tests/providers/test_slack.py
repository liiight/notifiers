import pytest

provider = 'slack'


class TestSlack(object):
    """
    Slack web hook tests

    Online test rely on setting the env variable NOTIFIERS_SLACK_WEBHOOK_URL
    """

    def test_slack_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://hooks.slack.com/services/',
            'name': 'slack',
            'site_url': 'https://api.slack.com/incoming-webhooks'
        }

    @pytest.mark.online
    def test_sanity(self, provider):
        data = {'message': 'foo'}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self, provider):
        data = {
            'message': 'http://foo.com',
            'icon_emoji': 'poop',
            'username': 'test',
            'channel': 'test',
            'attachments': [
                {
                    'title': 'attachment 1',
                    'title_link': 'https://github.com/liiight/notifiers',
                    'image_url': 'https://cdn.worldvectorlogo.com/logos/slack.svg',
                    'thumb_url': 'http://timelinethumbnailcreator.com/img/icon-brush-256.png',
                    'author_name': 'notifiers',
                    'author_link': 'https://github.com/liiight/notifiers',
                    'fallback': 'fallback text',
                    'text': 'attach this',
                    'footer': 'footer 1',
                    'pretext': 'pre-attach this',
                    'color': 'good',
                    'fields': [
                        {
                            'title': 'test_field1',
                            'value': 'test_value1',
                            'short': False
                        },
                        {
                            'title': 'test_field2',
                            'value': 'test_value2',
                            'short': True
                        }
                    ]
                },
                {
                    'title': 'attachment 2',
                    'title_link': 'https://github.com/liiight/notifiers',
                    'image_url': 'https://cdn.worldvectorlogo.com/logos/slack.svg',
                    'thumb_url': 'http://timelinethumbnailcreator.com/img/icon-brush-256.png',
                    'author_name': 'notifiers',
                    'author_link': 'https://github.com/liiight/notifiers',
                    'fallback': 'fallback text',
                    'text': 'attach this',
                    'footer': 'footer 1',
                    'pretext': 'pre-attach this',
                    'color': 'danger',
                    'fields': [
                        {
                            'title': 'test_field1',
                            'value': 'test_value1',
                            'short': False
                        },
                        {
                            'title': 'test_field2',
                            'value': 'test_value2',
                            'short': True
                        }
                    ]
                }
            ]

        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()
