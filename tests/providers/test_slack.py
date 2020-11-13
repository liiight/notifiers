import pytest

provider = "slack"


class TestSlack:
    """
    Slack web hook tests

    Online test rely on setting the env variable NOTIFIERS_SLACK_WEBHOOK_URL
    """

    @pytest.mark.online
    def test_sanity(self, provider, test_message):
        data = {"message": test_message}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self, provider):
        # todo add all blocks tests
        data = {
            "message": "http://foo.com",
            "attachments": [
                {
                    "title": "attachment 1",
                    "title_link": "https://github.com/liiight/notifiers",
                    "image_url": "https://cdn.worldvectorlogo.com/logos/slack.svg",
                    "thumb_url": "http://timelinethumbnailcreator.com/img/icon-brush-256.png",
                    "author_name": "notifiers",
                    "author_link": "https://github.com/liiight/notifiers",
                    "fallback": "fallback text",
                    "text": "attach this",
                    "footer": "footer 1",
                    "pretext": "pre-attach this",
                    "color": "good",
                    "fields": [
                        {
                            "title": "test_field1",
                            "value": "test_value1",
                            "short": False,
                        },
                        {"title": "test_field2", "value": "test_value2", "short": True},
                    ],
                },
                {
                    "title": "attachment 2",
                    "title_link": "https://github.com/liiight/notifiers",
                    "image_url": "https://cdn.worldvectorlogo.com/logos/slack.svg",
                    "thumb_url": "http://timelinethumbnailcreator.com/img/icon-brush-256.png",
                    "author_name": "notifiers",
                    "author_link": "https://github.com/liiight/notifiers",
                    "fallback": "fallback text",
                    "text": "attach this",
                    "footer": "footer 1",
                    "pretext": "pre-attach this",
                    "color": "danger",
                    "fields": [
                        {
                            "title": "test_field1",
                            "value": "test_value1",
                            "short": False,
                        },
                        {"title": "test_field2", "value": "test_value2", "short": True},
                    ],
                },
            ],
        }
        provider.notify(**data, raise_on_errors=True)
