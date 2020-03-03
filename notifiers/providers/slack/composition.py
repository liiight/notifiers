from enum import Enum
from typing import List
from typing import Type

from pydantic import constr
from pydantic import create_model
from pydantic import Field
from pydantic import HttpUrl

from notifiers.models.provider import SchemaModel


class SlackTextType(Enum):
    plain_text = "plain_text"
    markdown = "mrkdwn"


class SlackBlockTextObject(SchemaModel):
    """An object containing some text, formatted either as plain_text or using mrkdwn"""

    type: SlackTextType = Field(
        ..., description="The formatting to use for this text object"
    )
    text: constr(max_length=3000) = Field(
        ...,
        description="The text for the block. This field accepts any of the standard text"
        " formatting markup when type is mrkdwn",
    )
    emoji: bool = Field(
        None,
        description="Indicates whether emojis in a text field should be escaped into the colon emoji format. "
        "This field is only usable when type is plain_text",
    )
    verbatim: bool = Field(
        None,
        description="When set to false (as is default) URLs will be auto-converted into links,"
        " conversation names will be link-ified, and certain mentions will be automatically parsed."
        " Using a value of true will skip any preprocessing of this nature, although you can still"
        " include manual parsing strings. This field is only usable when type is mrkdwn.",
    )

    class Config:
        json_encoders = {SlackTextType: lambda v: v.value}


def _text_object_factory(
    max_length: int, type_: SlackTextType = None
) -> Type[SlackBlockTextObject]:
    """Returns a custom text object schema"""
    type_value = (SlackTextType, type_) if type_ else (SlackTextType, ...)
    return create_model(
        "CustomTextObject",
        type=type_value,
        text=(constr(max_length=max_length), ...),
        __base__=SlackBlockTextObject,
    )


class SlackOption(SchemaModel):
    """An object that represents a single selectable item in a select menu, multi-select menu, radio button group,
    or overflow menu."""

    text: _text_object_factory(type_=SlackTextType.plain_text, max_length=75) = Field(
        ...,
        description="A plain_text only text object that defines the text shown in the option on the menu."
        " Maximum length for the text in this field is 75 characters",
    )
    value: constr(max_length=75) = Field(
        ...,
        description="The string value that will be passed to your app when this option is chosen",
    )
    description: _text_object_factory(
        type_=SlackTextType.plain_text, max_length=75
    ) = Field(
        None,
        description="A plain_text only text object that defines a line of descriptive text shown below the "
        "text field beside the radio button.",
    )
    url: HttpUrl = Field(
        None,
        description="A URL to load in the user's browser when the option is clicked. "
        "The url attribute is only available in overflow menus. Maximum length for this field is 3000 characters. "
        "If you're using url, you'll still receive an interaction payload and will need to send an "
        "acknowledgement response.",
    )


class SlackOptionGroup(SchemaModel):
    """Provides a way to group options in a select menu or multi-select menu"""

    label: _text_object_factory(type_=SlackTextType.plain_text, max_length=75) = Field(
        ...,
        description="A plain_text only text object that defines the label shown above this group of options",
    )
    options: List[SlackOption] = Field(
        ...,
        description="An array of option objects that belong to this specific group. Maximum of 100 items",
        max_items=100,
    )


class SlackConfirmationDialog(SchemaModel):
    """An object that defines a dialog that provides a confirmation step to any interactive element.
     This dialog will ask the user to confirm their action by offering a confirm and deny buttons."""

    title: _text_object_factory(type_=SlackTextType.plain_text, max_length=100)
    text: _text_object_factory(max_length=300)
    confirm: _text_object_factory(max_length=30)
    deny: _text_object_factory(type_=SlackTextType.plain_text, max_length=30)


class SlackColor(Enum):
    good = "good"
    warning = "warning"
    danger = "danger"
