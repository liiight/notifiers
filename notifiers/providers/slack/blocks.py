from enum import Enum
from typing import List
from typing import Union

from pydantic import constr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator
from typing_extensions import Literal

from ...models.schema import ResourceSchema
from .elements import ButtonElement
from .elements import CheckboxElement
from .elements import DatePickerElement
from .elements import ExternalSelectElement
from .elements import ImageElement
from .elements import MultiSelectChannelsElement
from .elements import MultiSelectConversationsElement
from .elements import MultiSelectExternalMenuElement
from .elements import MultiSelectUserListElement
from .elements import MultiStaticSelectMenuElement
from .elements import OverflowElement
from .elements import RadioButtonGroupElement
from .elements import SelectChannelsElement
from .elements import SelectUsersElement
from .elements import StaticSelectElement
from notifiers.providers.slack.composition import _text_object_factory
from notifiers.providers.slack.composition import Text
from notifiers.providers.slack.composition import TextType

SectionBlockElements = Union[
    ButtonElement,
    CheckboxElement,
    DatePickerElement,
    ImageElement,
    MultiStaticSelectMenuElement,
    MultiSelectExternalMenuElement,
    MultiSelectUserListElement,
    MultiSelectConversationsElement,
    MultiSelectChannelsElement,
    OverflowElement,
    RadioButtonGroupElement,
    StaticSelectElement,
    ExternalSelectElement,
    SelectUsersElement,
    SelectChannelsElement,
]

ActionsBlockElements = Union[
    ButtonElement,
    CheckboxElement,
    DatePickerElement,
    OverflowElement,
    RadioButtonGroupElement,
    StaticSelectElement,
    ExternalSelectElement,
    SelectUsersElement,
    SelectChannelsElement,
]

ContextBlockElements = Union[ImageElement, Text]


class BlockType(str, Enum):
    section = "section"
    divider = "divider"
    image = "image"
    actions = "actions"
    context = "context"
    file = "file"


class BaseBlock(ResourceSchema):
    block_id: constr(max_length=255) = Field(
        None,
        description="A string acting as a unique identifier for a block. "
        "You can use this block_id when you receive an interaction payload to identify the source of "
        "the action. If not specified, one will be generated. Maximum length for this field is "
        "255 characters. block_id should be unique for each message and each iteration of a message. "
        "If a message is updated, use a new block_id",
    )


class SectionBlock(BaseBlock):
    """A section is one of the most flexible blocks available - it can be used as a simple text block,
    in combination with text fields, or side-by-side with any of the available block elements"""

    type: Literal[BlockType.section, BlockType.section.value] = Field(
        BlockType.section,
        description="The type of block. For a section block, type will always be section",
    )
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
    accessory: SectionBlockElements = Field(
        None, description="One of the available element objects"
    )

    @root_validator
    def text_or_field(cls, values):
        if not any(value in values for value in ("text", "fields")):
            raise ValueError("Either 'text' or 'fields' are required")
        return values


class DividerBlock(BaseBlock):
    """A content divider, like an <hr>, to split up different blocks inside of a message.
     The divider block is nice and neat, requiring only a type."""

    type: Literal[BlockType.divider, BlockType.divider.value] = Field(
        BlockType.divider,
        description="The type of block. For a divider block, type will always be divider",
    )


class ImageBlock(BaseBlock):
    """A simple image block, designed to make those cat photos really pop"""

    type: Literal[BlockType.image, BlockType.image.value] = Field(
        BlockType.image,
        description="The type of block. For a image block, type will always be image",
    )
    image_url: HttpUrl = Field(..., description="The URL of the image to be displayed")
    alt_text: constr(max_length=2000) = Field(
        ...,
        description="A plain-text summary of the image. This should not contain any markup",
    )
    title: _text_object_factory(
        "ImageText", max_length=2000, type=TextType.plain_text
    ) = Field(None, description="An optional title for the image")


class ActionsBlock(BaseBlock):
    """A block that is used to hold interactive elements"""

    type: Literal[BlockType.actions, BlockType.actions.value] = Field(
        BlockType.actions,
        description="The type of block. For an actions block, type will always be actions",
    )
    elements: List[ActionsBlockElements] = Field(
        ...,
        description="An array of interactive element objects - buttons, select menus, overflow menus, or date pickers",
        max_items=5,
    )


class ContextBlock(BaseBlock):
    """Displays message context, which can include both images and text"""

    type: Literal[BlockType.context, BlockType.context.value] = Field(
        BlockType.context,
        description="The type of block. For a context block, type will always be context",
    )
    elements: List[ContextBlockElements] = Field(
        ..., description="An array of image elements and text objects", max_items=10
    )


class FileBlock(BaseBlock):
    """Displays a remote file"""

    type: Literal[BlockType.file, BlockType.file.value] = Field(
        BlockType.file,
        description="The type of block. For a file block, type will always be file",
    )
    external_id: str = Field(..., description="The external unique ID for this file")
    source: Literal["remote"] = Field(
        "remote",
        description="At the moment, source will always be remote for a remote file",
    )


Blocks = Union[
    SectionBlock, DividerBlock, ImageBlock, ActionsBlock, ContextBlock, FileBlock,
]
