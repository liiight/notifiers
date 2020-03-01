from enum import Enum
from typing import List

from pydantic import constr
from pydantic import Field

from notifiers.models.provider import SchemaModel
from notifiers.providers.slack.composition import SlackBlockTextObject
from notifiers.providers.slack.elements import SlackElementTypes


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
    type = SlackBlockType.section
    text: SlackBlockTextObject = Field(
        None,
        description="The text for the block, in the form of a text object."
        " Maximum length for the text in this field is 3000 characters."
        " This field is not required if a valid array of fields objects is provided instead",
    )

    fields: List[SlackBlockTextObject] = Field(
        None,
        description="An array of text objects. Any text objects included with fields will be rendered in a compact "
        "format that allows for 2 columns of side-by-side text. Maximum number of items is 10."
        " Maximum length for the text in each item is 2000 characters",
        max_length=10,
    )
    accessory: SlackElementTypes = Field(
        None, description="One of the available element objects"
    )
