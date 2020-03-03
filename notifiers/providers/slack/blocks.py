from enum import Enum
from typing import List

from pydantic import constr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator
from typing_extensions import Literal

from notifiers.models.provider import SchemaModel
from notifiers.providers.slack.composition import _text_object_factory
from notifiers.providers.slack.composition import SlackTextType
from notifiers.providers.slack.elements import ActionsElements
from notifiers.providers.slack.elements import ContextElements
from notifiers.providers.slack.elements import SectionElements


class SlackBlockType(Enum):
    section = "section"
    divider = "divider"
    image = "image"
    actions = "actions"
    context = "context"
    file = "file"


class SlackBaseBlock(SchemaModel):
    type: SlackBlockType = Field(..., description="The type of block")
    block_id: constr(max_length=255) = Field(
        None,
        description="A string acting as a unique identifier for a block. "
        "You can use this block_id when you receive an interaction payload to identify the source of "
        "the action. If not specified, one will be generated. Maximum length for this field is "
        "255 characters. block_id should be unique for each message and each iteration of a message. "
        "If a message is updated, use a new block_id",
    )


class SlackSectionBlock(SlackBaseBlock):
    """A section is one of the most flexible blocks available - it can be used as a simple text block,
    in combination with text fields, or side-by-side with any of the available block elements"""

    type = SlackBlockType.section
    text: _text_object_factory("SectionBlockText", max_length=3000) = Field(
        None, description="The text for the block, in the form of a text object"
    )

    block_fields: List[
        _text_object_factory("SectionBlockFieldText", max_length=2000)
    ] = Field(
        None,
        description="An array of text objects. Any text objects included with fields will be rendered in a compact "
        "format that allows for 2 columns of side-by-side text",
        max_items=10,
        alias="fields",
    )
    accessory: SectionElements = Field(
        None, description="One of the available element objects"
    )

    @root_validator
    def text_or_field(cls, values):
        if not any(value in values for value in ("text", "fields")):
            raise ValueError("Either 'text' or 'fields' are required")
        return values


class SlackDividerBlock(SlackBaseBlock):
    """A content divider, like an <hr>, to split up different blocks inside of a message.
     The divider block is nice and neat, requiring only a type."""

    type = SlackBlockType.divider


class SlackImageBlock(SlackBaseBlock):
    """A simple image block, designed to make those cat photos really pop"""

    type = SlackBlockType.image
    image_url: HttpUrl = Field(..., description="The URL of the image to be displayed")
    alt_text: constr(max_length=2000) = Field(
        ...,
        description="A plain-text summary of the image. This should not contain any markup",
    )
    title: _text_object_factory(
        "ImageText", type_=SlackTextType.plain_text, max_length=2000
    ) = Field(None, description="An optional title for the image")


class SlackActionsBlock(SlackBaseBlock):
    """A block that is used to hold interactive elements"""

    type = SlackBlockType.actions
    elements: List[ActionsElements] = Field(
        ...,
        description="An array of interactive element objects - buttons, select menus, overflow menus, or date pickers",
        max_items=5,
    )


class SlackContextBlock(SlackBaseBlock):
    """Displays message context, which can include both images and text"""

    type = SlackBlockType.context
    elements: List[ContextElements] = Field(
        ..., description="An array of image elements and text objects", max_items=10
    )


class SlackFileBlock(SlackBaseBlock):
    """Displays a remote file"""

    type = SlackBlockType.file
    external_id: str = Field(..., description="The external unique ID for this file")
    source: Literal["remote"] = Field(
        "remote",
        description="At the moment, source will always be remote for a remote file",
    )
