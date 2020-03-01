from typing import List
from typing import Union

from pydantic import Field
from pydantic import HttpUrl
from pydantic import validator

from notifiers.models.provider import Provider
from notifiers.models.provider import SchemaModel
from notifiers.models.response import Response
from notifiers.providers.slack.blocks import SlackSectionBlock
from notifiers.providers.slack_ import SlackAttachmentSchema
from notifiers.utils import requests


class SlackSchema(SchemaModel):
    webhook_url: HttpUrl = Field(
        ...,
        description="The webhook URL to use. Register one at https://my.slack.com/services/new/incoming-webhook/",
    )
    message: str = Field(
        ...,
        description="The usage of this field changes depending on whether you're using blocks or not."
        " If you are, this is used as a fallback string to display in notifications."
        " If you aren't, this is the main body text of the message."
        " It can be formatted as plain text, or with mrkdwn."
        " This field is not enforced as required when using blocks, "
        "however it is highly recommended that you include it as the aforementioned fallback.",
        alias="text",
    )
    blocks: List[Union[SlackSectionBlock]] = Field(
        None,
        description="An array of layout blocks in the same format as described in the building blocks guide.",
        max_length=50,
    )
    attachments: List[SlackAttachmentSchema] = Field(
        None,
        description="An array of legacy secondary attachments. We recommend you use blocks instead.",
    )
    thread_ts: str = Field(
        None, description="The ID of another un-threaded message to reply to"
    )
    markdown: bool = Field(
        None,
        description="Determines whether the text field is rendered according to mrkdwn formatting or not."
        " Defaults to true",
        alias="mrkdwn",
    )
    icon_url: HttpUrl = Field(None, description="Override bot icon with image URL")
    icon_emoji: str = Field(None, description="Override bot icon with emoji name")
    username: str = Field(None, description="Override the displayed bot name")
    channel: str = Field(
        None, description="Override default channel or private message"
    )
    unfurl_links: bool = Field(
        None, description="Avoid or enable automatic attachment creation from URLs"
    )

    @validator("icon_emoji")
    def emoji(cls, v: str):
        return f':{v.strip(":")}:'


class Slack(Provider):
    """Send Slack webhook notifications"""

    base_url = "https://hooks.slack.com/services/"
    site_url = "https://api.slack.com/incoming-webhooks"
    name = "slack"

    schema_model = SlackSchema

    __fields = {
        "type": "array",
        "title": "Fields are displayed in a table on the message",
        "minItems": 1,
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "title": "Required Field Title"},
                "value": {
                    "type": "string",
                    "title": "Text value of the field. May contain standard message markup and must"
                    " be escaped as normal. May be multi-line",
                },
                "short": {
                    "type": "boolean",
                    "title": "Optional flag indicating whether the `value` is short enough to be displayed"
                    " side-by-side with other values",
                },
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    }
    __attachments = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "title": "Attachment title"},
                "author_name": {
                    "type": "string",
                    "title": "Small text used to display the author's name",
                },
                "author_link": {
                    "type": "string",
                    "title": "A valid URL that will hyperlink the author_name text mentioned above. "
                    "Will only work if author_name is present",
                },
                "author_icon": {
                    "type": "string",
                    "title": "A valid URL that displays a small 16x16px image to the left of the author_name text. "
                    "Will only work if author_name is present",
                },
                "title_link": {"type": "string", "title": "Attachment title URL"},
                "image_url": {"type": "string", "format": "uri", "title": "Image URL"},
                "thumb_url": {
                    "type": "string",
                    "format": "uri",
                    "title": "Thumbnail URL",
                },
                "footer": {"type": "string", "title": "Footer text"},
                "footer_icon": {
                    "type": "string",
                    "format": "uri",
                    "title": "Footer icon URL",
                },
                "ts": {
                    "type": ["integer", "string"],
                    "format": "timestamp",
                    "title": "Provided timestamp (epoch)",
                },
                "fallback": {
                    "type": "string",
                    "title": "A plain-text summary of the attachment. This text will be used in clients that don't"
                    " show formatted text (eg. IRC, mobile notifications) and should not contain any markup.",
                },
                "text": {
                    "type": "string",
                    "title": "Optional text that should appear within the attachment",
                },
                "pretext": {
                    "type": "string",
                    "title": "Optional text that should appear above the formatted data",
                },
                "color": {
                    "type": "string",
                    "title": "Can either be one of 'good', 'warning', 'danger', or any hex color code",
                },
                "fields": __fields,
            },
            "required": ["fallback"],
            "additionalProperties": False,
        },
    }
    _required = {"required": ["webhook_url", "message"]}
    _schema = {
        "type": "object",
        "properties": {
            "webhook_url": {
                "type": "string",
                "format": "uri",
                "title": "the webhook URL to use. Register one at https://my.slack.com/services/new/incoming-webhook/",
            },
            "icon_url": {
                "type": "string",
                "format": "uri",
                "title": "override bot icon with image URL",
            },
            "icon_emoji": {
                "type": "string",
                "title": "override bot icon with emoji name.",
            },
            "username": {"type": "string", "title": "override the displayed bot name"},
            "channel": {
                "type": "string",
                "title": "override default channel or private message",
            },
            "unfurl_links": {
                "type": "boolean",
                "title": "avoid automatic attachment creation from URLs",
            },
            "message": {
                "type": "string",
                "title": "This is the text that will be posted to the channel",
            },
            "attachments": __attachments,
        },
        "additionalProperties": False,
    }

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("webhook_url")
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
