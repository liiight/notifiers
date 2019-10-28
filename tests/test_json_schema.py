import hypothesis.strategies as st
import pytest
from hypothesis import given
from jsonschema import validate
from jsonschema import ValidationError

from notifiers.utils.schema.formats import format_checker
from notifiers.utils.schema.helpers import list_to_commas
from notifiers.utils.schema.helpers import one_or_more


class TestFormats:
    @pytest.mark.parametrize(
        "formatter, value",
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
        ],
    )
    def test_format_positive(self, formatter, value):
        validate(value, {"format": formatter}, format_checker=format_checker)

    def test_valid_file_format(self, tmpdir):
        file_1 = tmpdir.mkdir("foo").join("file_1")
        file_1.write("bar")

        validate(str(file_1), {"format": "valid_file"}, format_checker=format_checker)

    @pytest.mark.parametrize(
        "formatter, value",
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
            ("e164", "-14155552671"),
            ("e164", "+44207183875063673465"),
            ("e164", "+551155256325zdfgsd"),
        ],
    )
    def test_format_negative(self, formatter, value):
        with pytest.raises(ValidationError):
            validate(value, {"format": formatter}, format_checker=format_checker)


class TestSchemaUtils:
    @pytest.mark.parametrize(
        "input_schema, unique_items, min, max, data",
        [
            ({"type": "string"}, True, 1, 1, "foo"),
            ({"type": "string"}, True, 1, 2, ["foo", "bar"]),
            ({"type": "integer"}, True, 1, 2, 1),
            ({"type": "integer"}, True, 1, 2, [1, 2]),
        ],
    )
    def test_one_or_more_positive(self, input_schema, unique_items, min, max, data):
        expected_schema = one_or_more(input_schema, unique_items, min, max)
        validate(data, expected_schema)

    @pytest.mark.parametrize(
        "input_schema, unique_items, min, max, data",
        [
            ({"type": "string"}, True, 1, 1, 1),
            ({"type": "string"}, True, 1, 1, ["foo", "bar"]),
            ({"type": "integer"}, False, 3, None, [1, 1]),
            ({"type": "integer"}, True, 1, 1, [1, 2]),
        ],
    )
    def test_one_or_more_negative(self, input_schema, unique_items, min, max, data):
        expected_schema = one_or_more(input_schema, unique_items, min, max)
        with pytest.raises(ValidationError):
            validate(data, expected_schema)

    @given(st.lists(st.text()))
    def test_list_to_commas(self, input_data):
        assert list_to_commas(input_data) == ",".join(input_data)
