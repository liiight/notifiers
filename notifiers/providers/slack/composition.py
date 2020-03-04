from enum import Enum
from typing import List
from typing import Type

from pydantic import constr
from pydantic import create_model
from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator
from typing_extensions import Literal

from notifiers.models.provider import SchemaModel


class TextType(Enum):
    plain_text = "plain_text"
    markdown = "mrkdwn"


class Text(SchemaModel):
    """An object containing some text, formatted either as plain_text or using mrkdwn,
     our proprietary textual markup that's just different enough from Markdown to frustrate you"""

    type: TextType = Field(
        TextType.markdown, description="The formatting to use for this text object"
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

    @root_validator
    def check_emoji(cls, values):
        if values.get("emoji") and TextType(values["type"]) is not TextType.plain_text:
            raise ValueError("Cannot use 'emoji' when type is not 'plain_text'")
        return values

    class Config:
        json_encoders = {TextType: lambda v: v.value}


def _text_object_factory(
    model_name: str, max_length: int, type: TextType = None
) -> Type[Text]:
    """Returns a custom text object schema. If a `type_` is passed,
    it's enforced as the only possible value (both the enum and its value) and set as the default"""
    type_value = (Literal[type, type.value], type) if type else (TextType, ...)
    return create_model(
        model_name,
        type=type_value,
        text=(constr(max_length=max_length), ...),
        __base__=Text,
    )


class Option(SchemaModel):
    """An object that represents a single selectable item in a select menu, multi-select menu, radio button group,
    or overflow menu."""

    text: _text_object_factory(
        "OptionText", max_length=75, type=TextType.plain_text
    ) = Field(
        ...,
        description="A plain_text only text object that defines the text shown in the option on the menu."
        " Maximum length for the text in this field is 75 characters",
    )
    value: constr(max_length=75) = Field(
        ...,
        description="The string value that will be passed to your app when this option is chosen",
    )
    description: _text_object_factory(
        "DescriptionText", max_length=75, type=TextType.plain_text
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


class OptionGroup(SchemaModel):
    """Provides a way to group options in a select menu or multi-select menu"""

    label: _text_object_factory(
        "OptionGroupText", max_length=75, type=TextType.plain_text
    ) = Field(
        ...,
        description="A plain_text only text object that defines the label shown above this group of options",
    )
    options: List[Option] = Field(
        ...,
        description="An array of option objects that belong to this specific group. Maximum of 100 items",
        max_items=100,
    )


class ConfirmationDialog(SchemaModel):
    """An object that defines a dialog that provides a confirmation step to any interactive element.
     This dialog will ask the user to confirm their action by offering a confirm and deny buttons."""

    title: _text_object_factory(
        "DialogTitleText", max_length=100, type=TextType.plain_text
    )
    text: _text_object_factory("DialogTextText", max_length=300)
    confirm: _text_object_factory("DialogConfirmText", max_length=30)
    deny: _text_object_factory(
        "DialogDenyText", max_length=30, type=TextType.plain_text
    )


class Color(Enum):
    good = "good"
    warning = "warning"
    danger = "danger"
