from __future__ import annotations

from pydantic import Field

from ..core import Provider, Response
from ..models import SchemaModel, Timestamp, Url
from ..utils import requests


class SlackAttachmentField(SchemaModel):
    title: str = Field(description="Required Field Title")
    value: str | None = Field(
        None,
        description="Text value of the field. May contain standard message markup and must be escaped as normal. May be multi-line",
    )
    short: bool | None = Field(
        None,
        description="Optional flag indicating whether the `value` is short enough to be displayed side-by-side with other values",
    )


class SlackAttachment(SchemaModel):
    title: str | None = Field(None, description="Attachment title")
    author_name: str | None = Field(None, description="Small text used to display the author's name")
    author_link: str | None = Field(
        None,
        description="A valid URL that will hyperlink the author_name text mentioned above. Will only work if author_name is present",
    )
    author_icon: str | None = Field(
        None,
        description="A valid URL that displays a small 16x16px image to the left of the author_name text. Will only work if author_name is present",
    )
    title_link: str | None = Field(None, description="Attachment title URL")
    image_url: Url | None = Field(None, description="Image URL")
    thumb_url: Url | None = Field(None, description="Thumbnail URL")
    footer: str | None = Field(None, description="Footer text")
    footer_icon: Url | None = Field(None, description="Footer icon URL")
    ts: Timestamp | None = Field(None, description="Provided timestamp (epoch)")
    fallback: str = Field(
        description="A plain-text summary of the attachment. This text will be used in clients that don't"
        " show formatted text (eg. IRC, mobile notifications) and should not contain any markup.",
    )
    text: str | None = Field(None, description="Optional text that should appear within the attachment")
    pretext: str | None = Field(None, description="Optional text that should appear above the formatted data")
    color: str | None = Field(None, description="Can either be one of 'good', 'warning', 'danger', or any hex color code")
    fields: list[SlackAttachmentField] | None = Field(None, min_length=1, description="Fields are displayed in a table on the message")


class SlackSchema(SchemaModel):
    webhook_url: Url = Field(description="the webhook URL to use. Register one at https://my.slack.com/services/new/incoming-webhook/")
    icon_url: Url | None = Field(None, description="override bot icon with image URL")
    icon_emoji: str | None = Field(None, description="override bot icon with emoji name.")
    username: str | None = Field(None, description="override the displayed bot name")
    channel: str | None = Field(None, description="override default channel or private message")
    unfurl_links: bool | None = Field(None, description="avoid automatic attachment creation from URLs")
    message: str = Field(description="This is the text that will be posted to the channel")
    attachments: list[SlackAttachment] | None = Field(None)


class Slack(Provider):
    """Send Slack webhook notifications"""

    base_url = "https://hooks.slack.com/services/"
    site_url = "https://api.slack.com/incoming-webhooks"
    name = "slack"

    schema_model = SlackSchema

    def _prepare_data(self, data: dict) -> dict:
        text = data.pop("message")
        data["text"] = text
        if data.get("icon_emoji"):
            icon_emoji = data["icon_emoji"]
            if not icon_emoji.startswith(":"):
                icon_emoji = f":{icon_emoji}"
            if not icon_emoji.endswith(":"):
                icon_emoji += ":"
            data["icon_emoji"] = icon_emoji
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("webhook_url")
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
