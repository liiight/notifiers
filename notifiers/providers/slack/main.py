from datetime import datetime
from typing import List
from typing import Union

from pydantic import constr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator
from pydantic import validator
from pydantic.color import Color as ColorType

from notifiers.models.resource import Provider
from notifiers.models.response import Response
from notifiers.models.schema import ResourceSchema
from notifiers.providers.slack.blocks import Blocks
from notifiers.providers.slack.composition import Color
from notifiers.utils import requests


class FieldObject(ResourceSchema):
    title: str = Field(
        None,
        description="Shown as a bold heading displayed in the field object."
        " It cannot contain markup and will be escaped for you",
    )
    value: str = Field(
        None,
        description="The text value displayed in the field object. "
        "It can be formatted as plain text, or with mrkdwn by using the mrkdwn_in",
    )
    short: bool = Field(
        None,
        description="Indicates whether the field object is short enough to be "
        "displayed side-by-side with other field objects",
    )


class AttachmentSchema(ResourceSchema):
    """Secondary content can be attached to messages to include lower priority content - content that
     doesn't necessarily need to be seen to appreciate the intent of the message,
      but perhaps adds further context or additional information."""

    blocks: List[Blocks] = Field(
        None,
        description="An array of layout blocks in the same format as described in the building blocks guide.",
        max_items=50,
    )
    color: Union[Color, ColorType] = Field(
        None,
        description="Changes the color of the border on the left side of this attachment from the default gray",
    )
    author_icon: HttpUrl = Field(
        None,
        description="A valid URL that displays a small 16px by 16px image to the left of the author_name text."
        " Will only work if author_name is present",
    )
    author_link: HttpUrl = Field(
        None,
        description="A valid URL that will hyperlink the author_name text. Will only work if author_name is present.",
    )
    author_name: str = Field(
        None, description="Small text used to display the author's name"
    )
    fallback: str = Field(
        None,
        description="A plain text summary of the attachment used in clients that don't show "
        "formatted text (eg. IRC, mobile notifications)",
    )
    attachment_fields: List[FieldObject] = Field(
        None,
        description="An array of field objects that get displayed in a table-like way."
        " For best results, include no more than 2-3 field objects",
        min_items=1,
        alias="fields",
    )
    footer: constr(max_length=300) = Field(
        None,
        description="Some brief text to help contextualize and identify an attachment."
        " Limited to 300 characters, and may be truncated further when displayed to users in "
        "environments with limited screen real estate",
    )
    footer_icon: HttpUrl = Field(
        None,
        description="A valid URL to an image file that will be displayed beside the footer text. "
        "Will only work if author_name is present. We'll render what you provide at 16px by 16px. "
        "It's best to use an image that is similarly sized",
    )
    image_url: HttpUrl = Field(
        None,
        description="A valid URL to an image file that will be displayed at the bottom of the attachment."
        " We support GIF, JPEG, PNG, and BMP formats. "
        "Large images will be resized to a maximum width of 360px or a maximum height of 500px,"
        " while still maintaining the original aspect ratio. Cannot be used with thumb_url",
    )
    markdown_in: List[str] = Field(
        None,
        description="An array of field names that should be formatted by markdown syntax",
        alias="mrkdwn_in",
    )
    pretext: str = Field(
        None,
        description="Text that appears above the message attachment block. "
        "It can be formatted as plain text, or with mrkdwn by including it in the mrkdwn_in field",
    )
    text: str = Field(
        None,
        description="The main body text of the attachment. It can be formatted as plain text, "
        "or with mrkdwn by including it in the mrkdwn_in field."
        " The content will automatically collapse if it contains 700+ characters or 5+ linebreaks,"
        ' and will display a "Show more..." link to expand the content',
    )
    thumb_url: HttpUrl = Field(
        None,
        description="A valid URL to an image file that will be displayed as a thumbnail on the right side "
        "of a message attachment. We currently support the following formats: GIF, JPEG, PNG,"
        " and BMP. The thumbnail's longest dimension will be scaled down to 75px while maintaining "
        "the aspect ratio of the image. The filesize of the image must also be less than 500 KB."
        " For best results, please use images that are already 75px by 75px",
    )
    title: str = Field(
        None, description="Large title text near the top of the attachment"
    )
    title_link: HttpUrl = Field(
        None, description="A valid URL that turns the title text into a hyperlink"
    )
    timestamp: datetime = Field(
        None,
        description="A datetime that is used to related your attachment to a specific time."
        " The attachment will display the additional timestamp value as part of the attachment's footer. "
        "Your message's timestamp will be displayed in varying ways, depending on how far in the past "
        "or future it is, relative to the present. Form factors, like mobile versus desktop may "
        "also transform its rendered appearance",
        alias="ts",
    )

    @validator("color")
    def color_format(cls, v: Union[Color, ColorType]):
        return v.as_hex() if isinstance(v, ColorType) else v.value

    @validator("timestamp")
    def timestamp_format(cls, v: datetime):
        return v.timestamp()

    @root_validator
    def check_values(cls, values):
        if "blocks" not in values and not any(
            value in values for value in ("fallback", "text")
        ):
            raise ValueError("Either 'blocks' or 'fallback' or 'text' are required")
        return values


class SlackSchema(ResourceSchema):
    """Slack's webhook schema"""

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
    blocks: List[Blocks] = Field(
        None,
        description="An array of layout blocks in the same format as described in the building blocks guide.",
        max_items=50,
    )
    attachments: List[AttachmentSchema] = Field(
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


class Slack(Provider):
    """Send Slack webhook notifications"""

    base_url = "https://hooks.slack.com/services/"
    site_url = "https://api.slack.com/incoming-webhooks"
    name = "slack"

    schema_model = SlackSchema

    def _send_notification(self, data: SlackSchema) -> Response:
        payload = data.to_dict()
        response, errors = requests.post(data.webhook_url, json=payload)
        return self.create_response(payload, response, errors)
