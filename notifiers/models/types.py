"""
Reusable annotated types for provider schemas.

Each type validates without changing the value or its type (e.g. a valid file path stays a ``str``), so providers receive
the data as it was passed.
"""

from __future__ import annotations

import email.utils
import re
from datetime import date, datetime
from typing import Annotated, Any, Union

from pydantic import AfterValidator, Discriminator, Field, Tag
from pydantic_core import PydanticCustomError

from ..utils.helpers import valid_file

ISO8601 = re.compile(
    r"^(?P<full>("
    r"(?P<year>\d{4})([/-]?"
    r"(?P<mon>(0[1-9])|(1[012]))([/-]?"
    r"(?P<mday>(0[1-9])|([12]\d)|(3[01])))?)?(?:T"
    r"(?P<hour>([01][0-9])|(?:2[0123]))(:?"
    r"(?P<min>[0-5][0-9])(:?"
    r"(?P<sec>[0-5][0-9]([,.]\d{1,10})?))?)?"
    r"(?:Z|([\-+](?:([01][0-9])|(?:2[0123]))(:?(?:[0-5][0-9]))?))?)?))$"
)
E164_RE = re.compile(r"^\+?[1-9]\d{1,14}$")

_ONE = "__one__"
_MANY = "__many__"
UNION_TAGS = frozenset({_ONE, _MANY})
"""Discriminator tags used by :func:`one_or_more`. They're stripped from error locations"""


def _format_error(value: Any, fmt: str) -> PydanticCustomError:
    return PydanticCustomError("format", "{value} is not a '{format}'", {"value": repr(value), "format": fmt})


def _check_email(value: str) -> str:
    # Deliberately permissive: any value containing "@" is accepted, so unusual but valid addresses aren't rejected
    if "@" not in value:
        raise _format_error(value, "email")
    return value


def _check_iso8601(value: str) -> str:
    if not ISO8601.match(value):
        raise _format_error(value, "iso8601")
    return value


def _check_rfc2822(value: str) -> str:
    if email.utils.parsedate(value) is None:
        raise _format_error(value, "rfc2822")
    return value


def _check_ascii(value: str) -> str:
    if not value.isascii():
        raise _format_error(value, "ascii")
    return value


def _check_valid_file(value: str) -> str:
    if not valid_file(value):
        raise _format_error(value, "valid_file")
    return value


def _check_timestamp(value: int | str) -> int | str:
    try:
        number = int(value)
        datetime.fromtimestamp(number)
    except (ValueError, OverflowError, OSError):
        raise _format_error(value, "timestamp") from None
    if number < 0:
        raise _format_error(value, "timestamp")
    return value


def _check_e164(value: str) -> str:
    if not E164_RE.match(value):
        raise _format_error(value, "e164")
    return value


def _check_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError:
        raise _format_error(value, "date") from None
    return value


Email = Annotated[str, AfterValidator(_check_email)]
"""An email address. Only checks that the value contains an ``@``"""

Url = str
"""A URL. Kept as ``str`` and not validated, the provider's API is the authority on what it accepts"""

Hostname = str
"""A hostname. Not validated, connecting to the server is the authority on whether it's valid"""

Port = Annotated[int, Field(ge=0, le=65535)]
"""A TCP port number"""

Timestamp = Annotated[int | str, AfterValidator(_check_timestamp)]
"""A non negative Unix timestamp, as an integer or a numeric string"""

ISO8601Datetime = Annotated[str, AfterValidator(_check_iso8601)]
"""An ISO 8601 date/time string"""

RFC2822Datetime = Annotated[str, AfterValidator(_check_rfc2822)]
"""An RFC 2822 date/time string"""

DateString = Annotated[str, AfterValidator(_check_date)]
"""A ``YYYY-MM-DD`` date string"""

AsciiStr = Annotated[str, AfterValidator(_check_ascii)]
"""A string with only ASCII characters"""

FilePath = Annotated[str, AfterValidator(_check_valid_file)]
"""A path to an existing file. ``~`` is expanded for the check, the value is kept as given"""

E164 = Annotated[str, AfterValidator(_check_e164)]
"""A phone number in E.164 format"""


def _unique(values: list) -> list:
    seen: list = []
    for value in values:
        if value in seen:
            raise PydanticCustomError("unique_items", "{values} has non-unique elements", {"values": repr(values)})
        seen.append(value)
    return values


def _one_or_many(value: Any) -> str:
    return _MANY if isinstance(value, list | tuple) else _ONE


def one_or_more(item_type: Any, *, max_items: int | None = None, unique: bool = True) -> Any:
    """
    Builds a type that accepts either a single ``item_type`` value or a non empty list of them.
    The value's shape is preserved: a single value stays a single value, a tuple becomes a list.

    :param item_type: Type of a single item
    :param max_items: Maximum allowed number of items in the list form
    :param unique: Whether list items must be unique
    """
    list_type: Any = Annotated[list[item_type], Field(min_length=1, max_length=max_items)]
    if unique:
        list_type = Annotated[list_type, AfterValidator(_unique)]
    return Annotated[
        # typing.Union since `Annotated[...] | Annotated[...]` isn't supported on Python 3.10
        Union[Annotated[list_type, Tag(_MANY)], Annotated[item_type, Tag(_ONE)]],  # noqa: UP007
        Discriminator(_one_or_many),
    ]


class OneOrMore:
    """``OneOrMore[T]`` is shorthand for :func:`one_or_more(T) <one_or_more>`"""

    def __class_getitem__(cls, item_type: Any) -> Any:
        return one_or_more(item_type)
