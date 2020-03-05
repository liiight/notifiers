from enum import Enum
from typing import List
from typing import Union
from urllib.parse import urljoin

from pydantic import Field
from pydantic import HttpUrl
from pydantic import root_validator

from ..exceptions import ResourceError
from ..models.provider import Provider
from ..models.provider import ProviderResource
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests


class TelegramURL(HttpUrl):
    allowed_schemes = "http", "https", "tg"


class LoginUrl(SchemaModel):
    """This object represents a parameter of the inline keyboard button used to automatically authorize a user.
    Serves as a great replacement for the Telegram Login Widget when the user is coming from Telegram.
     All the user needs to do is tap/click a button and confirm that they want to log in"""

    url: HttpUrl = Field(
        ...,
        description="An HTTP URL to be opened with user authorization data added to the query string when the"
        " button is pressed. If the user refuses to provide authorization data, the original URL without"
        " information about the user will be opened. The data added is the same as described in"
        " Receiving authorization data",
    )
    forward_text: str = Field(
        None, description="New text of the button in forwarded messages"
    )
    bot_username: str = Field(
        None,
        description="Username of a bot, which will be used for user authorization. See Setting up a bot for"
        " more details. If not specified, the current bot's username will be assumed."
        " The url's domain must be the same as the domain linked with the bot",
    )
    request_write_access: bool = Field(
        None,
        description="Pass True to request the permission for your bot to send messages to the user",
    )


class InlineKeyboardButton(SchemaModel):
    """This object represents one button of an inline keyboard. You must use exactly one of the optional fields"""

    text: str = Field(..., description="Label text on the button")
    url: TelegramURL = Field(
        None, description="HTTP or tg:// url to be opened when button is pressed"
    )
    login_url: LoginUrl = Field(
        None,
        description="An HTTP URL used to automatically authorize the user. Can be used as a replacement for the"
        " Telegram Login Widget",
    )
    callback_data: str = Field(
        None,
        description="Data to be sent in a callback query to the bot when button is pressed",
    )
    switch_inline_query: str = Field(
        None,
        description="If set, pressing the button will prompt the user to select one of their chats, "
        "open that chat and insert the bot‘s username and the specified inline query in the input field."
        " Can be empty, in which case just the bot’s username will be inserted",
    )
    switch_inline_query_current_chat: str = Field(
        None,
        description="If set, pressing the button will insert the bot‘s username and the specified inline query in the"
        " current chat's input field. Can be empty, in which case only the bot’s username will be inserted",
    )
    callback_game: str = Field(
        None,
        description="Description of the game that will be launched when the user presses the button",
    )
    pay: bool = Field(None, description="Specify True, to send a Pay button")

    @root_validator
    def only_one_optional(cls, values):
        values_items = set(values.keys())
        values_items.remove("text")
        if len(values_items) > 1:
            raise ValueError("You must use exactly one of the optional fields")
        return values


class KeyboardButtonPollType(SchemaModel):
    type: str = Field(
        None,
        description="If quiz is passed, the user will be allowed to create only polls in the quiz mode."
        " If regular is passed, only regular polls will be allowed. Otherwise, the user will be allowed"
        " to create a poll of any type",
    )


class KeyboardButton(SchemaModel):
    """This object represents one button of the reply keyboard. For simple text buttons String can be
    used instead of this object to specify text of the button. Optional fields request_contact,
    request_location, and request_poll are mutually exclusive"""

    text: str = Field(
        ...,
        description="Text of the button. If none of the optional fields are used, it will be sent as a message "
        "when the button is pressed",
    )
    request_contact: bool = Field(
        None,
        description="If True, the user's phone number will be sent as a contact when the button is pressed."
        " Available in private chats only",
    )
    request_location: bool = Field(
        None,
        description="If True, the user's current location will be sent when the button is pressed."
        " Available in private chats only",
    )
    request_poll: KeyboardButtonPollType = Field(
        None,
        description="If specified, the user will be asked to create a poll and send it to the bot when the button "
        "is pressed. Available in private chats only",
    )


class InlineKeyboardMarkup(SchemaModel):
    """This object represents an inline keyboard that appears right next to the message it belongs to"""

    inline_keyboard: List[List[InlineKeyboardButton]] = Field(
        ...,
        description="Array of button rows, each represented by an Array of InlineKeyboardButton objects",
    )


class ReplyKeyboardMarkup(SchemaModel):
    """This object represents a custom keyboard with reply options
     (see Introduction to bots for details and examples)"""

    keyboard: List[List[KeyboardButton]] = Field(
        ...,
        description="Array of button rows, each represented by an Array of KeyboardButton objects",
    )
    resize_keyboard: bool = Field(
        None,
        description="Requests clients to resize the keyboard vertically for optimal fit "
        "(e.g., make the keyboard smaller if there are just two rows of buttons)."
        " Defaults to false, in which case the custom keyboard is always of the same"
        " height as the app's standard keyboard",
    )
    one_time_keyboard: bool = Field(
        None,
        description="Requests clients to hide the keyboard as soon as it's been used."
        " The keyboard will still be available, but clients will automatically display the usual "
        "letter-keyboard in the chat – the user can press a special button in the input field to see "
        "the custom keyboard again. Defaults to false",
    )
    selective: bool = Field(
        None,
        description="Use this parameter if you want to show the keyboard to specific users only. Targets: 1)"
        " users that are @mentioned in the text of the Message object; 2) if the bot's message is a "
        "reply (has reply_to_message_id), sender of the original message. Example: A user requests to "
        "change the bot‘s language, bot replies to the request with a keyboard to select the new language."
        " Other users in the group don’t see the keyboard",
    )


class ReplyKeyboardRemove(SchemaModel):
    """Upon receiving a message with this object, Telegram clients will remove the current custom keyboard and
     display the default letter-keyboard. By default, custom keyboards are displayed until a new keyboard is sent by
     a bot. An exception is made for one-time keyboards that are hidden immediately after the user presses a button
     (see ReplyKeyboardMarkup)."""

    remove_keyboard: bool = Field(
        ...,
        description="Requests clients to remove the custom keyboard (user will not be able to summon this keyboard; "
        "if you want to hide the keyboard from sight but keep it accessible, use one_time_keyboard in"
        " ReplyKeyboardMarkup",
    )
    selective: bool = Field(
        None,
        description="Use this parameter if you want to remove the keyboard for specific users only."
        " Targets: 1) users that are @mentioned in the text of the Message object; "
        "2) if the bot's message is a reply (has reply_to_message_id),"
        " sender of the original message. Example: A user votes in a poll,"
        " bot returns confirmation message in reply to the vote and removes the keyboard for that user,"
        " while still showing the keyboard with poll options to users who haven't voted yet",
    )


class ForceReply(SchemaModel):
    """Upon receiving a message with this object, Telegram clients will display a reply interface to the user
     (act as if the user has selected the bot‘s message and tapped ’Reply').
      This can be extremely useful if you want to create user-friendly step-by-step interfaces without having
       to sacrifice privacy mode."""

    force_reply: bool = Field(
        ...,
        description="Shows reply interface to the user, as if they manually selected the bot‘s message and"
        " tapped ’Reply'",
    )
    selective: bool = Field(
        None,
        description="Use this parameter if you want to force reply from specific users only. "
        "Targets: 1) users that are @mentioned in the text of the Message object; "
        "2) if the bot's message is a reply (has reply_to_message_id), sender of the original message",
    )


class ParseMode(Enum):
    markdown = "Markdown"
    html = "HTML"
    markdown_v2 = "MarkdownV2"


class TelegramBaseSchema(SchemaModel):
    token: str = Field(..., description="Bot token")


class TelegramSchema(TelegramBaseSchema):
    message: str = Field(
        ...,
        description="Text of the message to be sent, 1-4096 characters after entities parsing",
        alias="text",
    )
    parse_mode: ParseMode = Field(
        None,
        description="Send Markdown or HTML, if you want Telegram apps to show bold, italic, "
        "fixed-width text or inline URLs in your bot's message.",
    )
    disable_web_page_preview: bool = Field(
        None, description="Disables link previews for links in this message"
    )
    disable_notification: bool = Field(
        None,
        description="Sends the message silently. Users will receive a notification with no sound",
    )
    reply_to_message_id: int = Field(
        None, description="If the message is a reply, ID of the original message"
    )
    reply_markup: Union[
        InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
    ] = Field(
        None,
        description="Additional interface options. A JSON-serialized object for an inline keyboard,"
        " custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user",
    )


class TelegramMixin:
    """Shared resources between :class:`TelegramUpdates` and :class:`Telegram`"""

    base_url = "https://api.telegram.org/bot{token}"
    name = "telegram"
    path_to_errors = ("description",)


class TelegramUpdates(TelegramMixin, ProviderResource):
    """Return Telegram bot updates, correlating to the `getUpdates` method. Returns chat IDs needed to notifications"""

    resource_name = "updates"
    schema_model = TelegramBaseSchema

    def _get_resource(self, data: TelegramBaseSchema) -> list:
        url = urljoin(self.base_url.format(token=data.token), "/getUpdates")
        response, errors = requests.get(url, path_to_errors=self.path_to_errors)
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return response.json()["result"]


class Telegram(TelegramMixin, Provider):
    """Send Telegram notifications"""

    site_url = "https://core.telegram.org/"
    _resources = {"updates": TelegramUpdates()}
    schema_model = TelegramSchema

    def _send_notification(self, data: TelegramSchema) -> Response:
        url = urljoin(self.base_url.format(token=data.token), "/sendMessage")
        payload = data.to_dict(exclude={"token"})
        response, errors = requests.post(
            url, json=payload, path_to_errors=self.path_to_errors
        )
        return self.create_response(payload, response, errors)
