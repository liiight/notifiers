from datetime import date
from enum import Enum
from typing import List
from typing import Union

from pydantic import conint
from pydantic import constr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import PositiveInt
from pydantic import root_validator
from pydantic import validator

from notifiers.models.provider import SchemaModel
from notifiers.providers.slack.composition import _text_object_factory
from notifiers.providers.slack.composition import SlackConfirmationDialog
from notifiers.providers.slack.composition import SlackOption
from notifiers.providers.slack.composition import SlackOptionGroup
from notifiers.providers.slack.composition import SlackTextType


class SlackElementType(Enum):
    button = "button"
    checkboxes = "checkboxes"
    date_picker = "datepicker"
    image = "image"
    overflow = "overflow"
    plain_text_input = "plain_text_input"
    radio_buttons = "radio_buttons"

    multi_static_select = "multi_static_select"
    multi_external_select = "multi_external_select"
    multi_users_select = "multi_users_select"
    multi_conversations_select = "multi_conversations_select"
    multi_channels_select = "multi_channels_select"

    static_select = "static_select"
    external_select = "external_select"
    conversations_select = "conversations_select"
    users_select = "users_select"
    channels_select = "channels_select"


class SlackBaseElement(SchemaModel):
    type: SlackElementType = Field(..., description="The type of element")
    action_id: constr(max_length=255) = Field(
        ...,
        description="An identifier for this action. You can use this when you receive an interaction payload to "
        "identify the source of the action. Should be unique among all other action_ids used "
        "elsewhere by your app",
    )

    class Config:
        json_encoders = {SlackElementType: lambda v: v.value}


class SlackButtonElementStyle(Enum):
    primary = "primary"
    danger = "danger"
    default = None


class SlackButtonElement(SlackBaseElement):
    """An interactive component that inserts a button.
     The button can be a trigger for anything from opening a simple link to starting a complex workflow."""

    type = SlackElementType.button
    text: _text_object_factory(type_=SlackTextType.plain_text, max_length=75)
    url: HttpUrl = Field(
        None,
        description="A URL to load in the user's browser when the button is clicked. "
        "Maximum length for this field is 3000 characters. If you're using url,"
        " you'll still receive an interaction payload and will need to send an acknowledgement response",
    )
    value: constr(max_length=2000) = Field(
        None,
        description="The value to send along with the interaction payload. "
        "Maximum length for this field is 2000 characters",
    )
    style: SlackButtonElementStyle = Field(
        None,
        description="Decorates buttons with alternative visual color schemes. Use this option with restraint",
    )
    confirm: SlackConfirmationDialog = Field(
        None,
        description="A confirm object that defines an optional confirmation dialog after the button is clicked.",
    )


class SlackCheckboxElement(SlackBaseElement):
    """A checkbox group that allows a user to choose multiple items from a list of possible options"""

    type = SlackElementType.checkboxes
    options: List[SlackOption] = Field(..., description="An array of option objects")
    initial_options: List[SlackOption] = Field(
        ...,
        description="An array of option objects that exactly matches one or more of the options within options."
        " These options will be selected when the checkbox group initially loads",
    )
    confirm: SlackConfirmationDialog = Field(
        None,
        description="A confirm object that defines an optional confirmation dialog that appears after "
        "clicking one of the checkboxes in this element.",
    )


class SlackDatePickerElement(SlackBaseElement):
    """An element which lets users easily select a date from a calendar style UI."""

    placeholder: _text_object_factory(
        type_=SlackTextType.plain_text, max_length=150
    ) = Field(
        None,
        description="A plain_text only text object that defines the placeholder text shown on the datepicker."
        " Maximum length for the text in this field is 150 characters",
    )
    initial_date: date = Field(
        None, description="The initial date that is selected when the element is loaded"
    )
    confirm: SlackConfirmationDialog = Field(
        None,
        description="A confirm object that defines an optional confirmation dialog that appears"
        " after a date is selected.",
    )

    @validator("initial_date")
    def format_date(cls, v: date):
        return str(v)


class SlackImageElement(SlackBaseElement):
    """A plain-text summary of the image. This should not contain any markup"""

    type = SlackElementType.image
    image_url: HttpUrl = Field(..., description="The URL of the image to be displayed")
    alt_text: str = Field(
        ...,
        description="A plain-text summary of the image. This should not contain any markup",
    )


class SlackMultiSelectBaseElement(SlackBaseElement):
    placeholder: _text_object_factory(
        type_=SlackTextType.plain_text, max_length=150
    ) = Field(
        ...,
        description="A plain_text only text object that defines the placeholder text shown on the menu",
    )
    initial_options: List[SlackOption] = Field(
        None,
        description="An array of option objects that exactly match one or more of the options within options "
        "or option_groups. These options will be selected when the menu initially loads.",
    )
    confirm: SlackConfirmationDialog = Field(
        None,
        description="A confirm object that defines an optional confirmation dialog that appears before "
        "the multi-select choices are submitted",
    )
    max_selected_items: PositiveInt = Field(
        None,
        description="Specifies the maximum number of items that can be selected in the menu",
    )


class SlackMultiStaticSelectMenuElement(SlackMultiSelectBaseElement):
    """This is the simplest form of select menu, with a static list of options passed in when defining the element."""

    type = SlackElementType.multi_static_select

    options: List[SlackOption] = Field(
        None, description="An array of option objects.", max_items=100
    )
    option_groups: List[SlackOptionGroup] = Field(
        None, description="An array of option group objects", max_items=100
    )

    @root_validator
    def option_check(cls, values):
        if not any(value in values for value in ("options", "option_groups")):
            raise ValueError("Either 'options' or 'option_groups' are required")

        if all(value in values for value in ("options", "option_groups")):
            raise ValueError("Cannot use both 'options' and 'option_groups'")
        return values


class SlackMultiSelectExternalMenuElement(SlackMultiSelectBaseElement):
    """This menu will load its options from an external data source, allowing for a dynamic list of options."""

    type = SlackElementType.multi_external_select
    min_query_length: PositiveInt = Field(
        None,
        description="When the typeahead field is used, a request will be sent on every character change. "
        "If you prefer fewer requests or more fully ideated queries, use the min_query_length attribute"
        " to tell Slack the fewest number of typed characters required before dispatch",
    )


class SlackMultiSelectUserListElement(SlackMultiSelectBaseElement):
    """This multi-select menu will populate its options with a list of Slack users visible to the
    current user in the active workspace."""

    type = SlackElementType.multi_users_select
    initial_users: List[str] = Field(
        None,
        description="An array of user IDs of any valid users to be pre-selected when the menu loads.",
    )


class SlackMultiSelectConversationsElement(SlackMultiSelectBaseElement):
    """This multi-select menu will populate its options with a list of public and private channels,
    DMs, and MPIMs visible to the current user in the active workspace"""

    type = SlackElementType.multi_conversations_select
    initial_conversations: List[str] = Field(
        None,
        description="An array of one or more IDs of any valid conversations to be pre-selected when the menu loads",
    )


class SlackMultiSelectChannelsElement(SlackMultiSelectBaseElement):
    """This multi-select menu will populate its options with a list of public channels visible to the current
     user in the active workspace"""

    type = SlackElementType.multi_channels_select
    initial_channels: List[str] = Field(
        None,
        description="An array of one or more IDs of any valid public channel to be pre-selected when the menu loads",
    )


class SlackOverflowElement(SlackBaseElement):
    """This is like a cross between a button and a select menu - when a user clicks on this overflow button,
    they will be presented with a list of options to choose from. Unlike the select menu,
     there is no typeahead field, and the button always appears with an ellipsis ("…") rather than customisable text."""

    type = SlackElementType.overflow
    options: List[SlackOption] = Field(
        ...,
        description="An array of option objects to display in the menu",
        min_items=2,
        max_items=5,
    )
    confirm: SlackConfirmationDialog = Field(
        None,
        description="A confirm object that defines an optional confirmation dialog that appears after a menu "
        "item is selected",
    )


class SlackPlainTextInputElement(SlackBaseElement):
    """A plain-text input, similar to the HTML <input> tag, creates a field where a user can enter freeform data.
    It can appear as a single-line field or a larger textarea using the multiline flag."""

    type = SlackElementType.plain_text_input
    placeholder: _text_object_factory(
        type_=SlackTextType.plain_text, max_length=150
    ) = Field(
        None,
        description="A plain_text only text object that defines the placeholder text shown in the plain-text input",
    )
    initial_value: str = Field(
        None, description="The initial value in the plain-text input when it is loaded"
    )
    multiline: bool = Field(
        None,
        description="Indicates whether the input will be a single line (false) or a larger textarea (true)",
    )
    min_length: conint(gt=0, le=3000) = Field(
        None,
        description="The minimum length of input that the user must provide. If the user provides less,"
        " they will receive an error",
    )
    max_length: PositiveInt = Field(
        None,
        description="The maximum length of input that the user can provide. If the user provides more,"
        " they will receive an error",
    )


class SlackRadioButtonGroupElement(SlackBaseElement):
    """A radio button group that allows a user to choose one item from a list of possible options"""

    type = SlackElementType.radio_buttons
    options: List[SlackOption] = Field(..., description="An array of option objects")
    initial_option: SlackOption = Field(
        None,
        description="An option object that exactly matches one of the options within options."
        " This option will be selected when the radio button group initially loads.",
    )
    confirm: SlackConfirmationDialog = Field(
        None,
        description="A confirm object that defines an optional confirmation dialog that appears after "
        "clicking one of the radio buttons in this element",
    )


class SlackStaticSelectElement(SlackMultiStaticSelectMenuElement):
    """This is the simplest form of select menu, with a static list of options passed in when defining the element"""

    type = SlackElementType.static_select


class SlackExternalSelectElement(SlackMultiSelectExternalMenuElement):
    """This select menu will load its options from an external data source, allowing for a dynamic list of options"""

    type = SlackElementType.external_select


class SlackSelectConversationsElement(SlackMultiSelectConversationsElement):
    """This select menu will populate its options with a list of public and private channels,
     DMs, and MPIMs visible to the current user in the active workspace."""

    type = SlackElementType.conversations_select


class SlackSelectChannelsElement(SlackMultiSelectChannelsElement):
    """This select menu will populate its options with a list of public channels visible to the current user
     in the active workspace."""

    type = SlackElementType.channels_select


class SlackSelectUsersElement(SlackMultiSelectUserListElement):
    """This select menu will populate its options with a list of Slack users visible to the
     current user in the active workspace"""

    type = SlackElementType.users_select


SectionElements = Union[
    SlackButtonElement,
    SlackCheckboxElement,
    SlackDatePickerElement,
    SlackImageElement,
    SlackMultiStaticSelectMenuElement,
    SlackMultiSelectExternalMenuElement,
    SlackMultiSelectUserListElement,
    SlackMultiSelectConversationsElement,
    SlackMultiSelectChannelsElement,
    SlackOverflowElement,
    SlackPlainTextInputElement,
    SlackRadioButtonGroupElement,
    SlackStaticSelectElement,
    SlackExternalSelectElement,
    SlackSelectUsersElement,
    SlackSelectChannelsElement,
]
ActionsElements = Union[
    SlackButtonElement,
    SlackCheckboxElement,
    SlackDatePickerElement,
    SlackOverflowElement,
    SlackPlainTextInputElement,
    SlackRadioButtonGroupElement,
    SlackStaticSelectElement,
    SlackExternalSelectElement,
    SlackSelectUsersElement,
    SlackSelectChannelsElement,
]
InputElements = Union[
    SlackCheckboxElement,
    SlackDatePickerElement,
    SlackMultiStaticSelectMenuElement,
    SlackMultiSelectExternalMenuElement,
    SlackMultiSelectUserListElement,
    SlackMultiSelectConversationsElement,
    SlackMultiSelectChannelsElement,
    SlackPlainTextInputElement,
    SlackRadioButtonGroupElement,
    SlackStaticSelectElement,
    SlackExternalSelectElement,
    SlackSelectUsersElement,
    SlackSelectChannelsElement,
]
ContextElements = Union[SlackImageElement]
