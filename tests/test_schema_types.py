"""Tests for the pydantic schema base model, field types and helpers"""

from __future__ import annotations

import hypothesis.strategies as st
import pytest
from hypothesis import given
from pydantic import Field, TypeAdapter, ValidationError, model_validator
from pydantic_core import PydanticCustomError

from notifiers.models import E164, AsciiStr, DateString, Email, FilePath, ISO8601Datetime, OneOrMore, Port, RFC2822Datetime, SchemaModel, Timestamp, one_or_more
from notifiers.models.base import format_validation_error, model_defaults, required_fields
from notifiers.utils.helpers import list_to_commas

FORMATS = {
    "iso8601": ISO8601Datetime,
    "rfc2822": RFC2822Datetime,
    "ascii": AsciiStr,
    "port": Port,
    "timestamp": Timestamp,
    "e164": E164,
    "email": Email,
    "date": DateString,
}


class TestFormats:
    @pytest.mark.parametrize(
        ("formatter", "value"),
        [
            ("iso8601", "2018-07-15T07:39:59+00:00"),
            ("iso8601", "2018-07-15T07:39:59Z"),
            ("iso8601", "20180715T073959Z"),
            ("rfc2822", "Thu, 25 Dec 1975 14:15:16 -0500"),
            ("ascii", "foo"),
            ("port", "44444"),
            ("port", 44_444),
            ("timestamp", 1531644024),
            ("timestamp", "1531644024"),
            ("e164", "+14155552671"),
            ("e164", "+442071838750"),
            ("e164", "+551155256325"),
            ("email", "foo@bar.com"),
            ("date", "2020-01-31"),
        ],
    )
    def test_format_positive(self, formatter, value):
        TypeAdapter(FORMATS[formatter]).validate_python(value)

    @pytest.mark.parametrize(
        ("formatter", "value"),
        [
            ("iso8601", "2018-14-15T07:39:59+00:00"),
            ("iso8601", "2018-07-15T07:39:59Z~"),
            ("iso8601", "20180715T0739545639Z"),
            ("rfc2822", "Thu 25 Dec14:15:16 -0500"),
            ("ascii", "פו"),
            ("port", "70000"),
            ("port", 70_000),
            ("timestamp", "15565-5631644024"),
            ("timestamp", "155655631644024"),
            ("timestamp", -1),
            ("e164", "-14155552671"),
            ("e164", "+44207183875063673465"),
            ("e164", "+551155256325zdfgsd"),
            ("email", "foo"),
            ("date", "2020-13-01"),
        ],
    )
    def test_format_negative(self, formatter, value):
        with pytest.raises(ValidationError):
            TypeAdapter(FORMATS[formatter]).validate_python(value)

    def test_formats_keep_original_value(self):
        """Format types validate without changing the value, so data passed to providers is unchanged"""
        assert TypeAdapter(Timestamp).validate_python("1531644024") == "1531644024"
        assert TypeAdapter(Timestamp).validate_python(1531644024) == 1531644024
        assert TypeAdapter(Email).validate_python("foo@bar.com ") == "foo@bar.com "

    def test_valid_file_format(self, tmpdir):
        file_1 = tmpdir.mkdir("foo").join("file_1")
        file_1.write("bar")
        assert TypeAdapter(FilePath).validate_python(str(file_1)) == str(file_1)
        with pytest.raises(ValidationError, match="is not a 'valid_file'"):
            TypeAdapter(FilePath).validate_python(str(tmpdir.join("nope")))


class TestOneOrMore:
    @pytest.mark.parametrize(
        ("item_type", "unique", "max_items", "data"),
        [
            (str, True, 1, "foo"),
            (str, True, 2, ["foo", "bar"]),
            (int, True, 2, 1),
            (int, True, 2, [1, 2]),
            (int, False, None, [1, 1]),
        ],
    )
    def test_one_or_more_positive(self, item_type, unique, max_items, data):
        assert TypeAdapter(one_or_more(item_type, unique=unique, max_items=max_items)).validate_python(data) == data

    @pytest.mark.parametrize(
        ("item_type", "unique", "max_items", "data"),
        [
            (str, True, 1, 1),
            (str, True, 1, ["foo", "bar"]),
            (int, True, None, [1, 1]),
            (int, True, 1, [1, 2]),
            (str, True, None, []),
        ],
    )
    def test_one_or_more_negative(self, item_type, unique, max_items, data):
        with pytest.raises(ValidationError):
            TypeAdapter(one_or_more(item_type, unique=unique, max_items=max_items)).validate_python(data)

    def test_shape_is_preserved(self):
        adapter = TypeAdapter(OneOrMore[str])
        assert adapter.validate_python("foo") == "foo"
        assert adapter.validate_python(["foo"]) == ["foo"]
        assert adapter.validate_python(("foo", "bar")) == ["foo", "bar"]

    @given(st.lists(st.text()))
    def test_list_to_commas(self, input_data):
        assert list_to_commas(input_data) == ",".join(input_data)


class _Schema(SchemaModel):
    a: str | None = None
    b: str | None = None
    c: str | None = None
    d: str | None = None
    from_: str | None = Field(None, alias="from")
    device_id: str | None = Field(None, alias="deviceId")
    required_one: str
    with_default: int = 5

    @model_validator(mode="after")
    def _rules(self):
        self.require_dependencies({"a": ["b"], "from_": ["device_id"]})
        if self.is_set("c") and self.is_set("d"):
            raise PydanticCustomError("c_or_d", "Only one of 'c' or 'd' is allowed")
        return self


class TestSchemaModel:
    @pytest.mark.parametrize(
        ("data", "message"),
        [
            ({}, "'required_one' is a required property"),
            ({"required_one": "x", "a": "x"}, "'b' is a dependency of 'a'"),
            ({"required_one": "x", "from": "x"}, "'deviceId' is a dependency of 'from'"),
            ({"required_one": "x", "c": "x", "d": "x"}, "Only one of 'c' or 'd' is allowed"),
            ({"required_one": "x", "zzz": 1}, "Additional properties are not allowed ('zzz' was unexpected)"),
            ({"required_one": "x", "with_default": "nope"}, "'with_default': Input should be a valid integer, unable to parse string as an integer"),
        ],
    )
    def test_validation_messages(self, data, message):
        with pytest.raises(ValidationError) as e:
            _Schema.model_validate(data)
        assert format_validation_error(e.value) == message

    def test_valid(self):
        assert _Schema.model_validate({"required_one": "x", "a": "x", "b": "y", "c": "x"})

    def test_none_counts_as_not_set(self):
        assert _Schema.model_validate({"required_one": "x", "a": None})

    @pytest.mark.parametrize("data", [{"from": "x", "deviceId": "y"}, {"from_": "x", "device_id": "y"}])
    def test_populate_by_name_or_alias(self, data):
        model = _Schema.model_validate({"required_one": "x", **data})
        assert (model.from_, model.device_id) == ("x", "y")
        assert model.model_dump(by_alias=True, exclude_unset=True) == {"required_one": "x", "from": "x", "deviceId": "y"}

    def test_required_fields(self):
        assert required_fields(_Schema) == ["required_one"]

    def test_model_defaults(self):
        assert model_defaults(_Schema) == {"with_default": 5}
        assert model_defaults(_Schema, keys=set()) == {}
