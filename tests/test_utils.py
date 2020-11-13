import pytest

from notifiers.models.schema import ResourceSchema
from notifiers.utils.helpers import dict_from_environs
from notifiers.utils.helpers import merge_dicts
from notifiers.utils.helpers import snake_to_camel_case
from notifiers.utils.requests import file_list_for_request


class TypeTest(ResourceSchema):
    string = ""
    integer = 0
    float_ = 0.1
    bool_ = True
    bytes = b""


class TestHelpers:
    @pytest.mark.parametrize(
        "target_dict, merge_dict, result",
        [
            ({"a": "foo"}, {"b": "bar"}, {"a": "foo", "b": "bar"}),
            ({"a": "foo"}, {"a": "bar"}, {"a": "foo"}),
        ],
    )
    def test_merge_dict(self, target_dict, merge_dict, result):
        assert merge_dicts(target_dict, merge_dict) == result

    @pytest.mark.parametrize(
        "prefix, name, args, result",
        [("foo", "bar", ["key1", "key2"], {"key1": "baz", "key2": "baz"})],
    )
    def test_dict_from_environs(self, prefix, name, args, result, monkeypatch):
        for arg in args:
            environ = f"{prefix}_{name}_{arg}".upper()
            monkeypatch.setenv(environ, "baz")
        assert dict_from_environs(prefix, name, args) == result

    @pytest.mark.parametrize(
        "snake_value, cc_value",
        [
            ("foo_bar", "FooBar"),
            ("foo", "Foo"),
            ("long_ass_var_name", "LongAssVarName"),
        ],
    )
    def test_snake_to_camel_case(self, snake_value, cc_value):
        assert snake_to_camel_case(snake_value) == cc_value

    def test_file_list_for_request(self, tmp_path):
        file_1 = tmp_path / "file_1"
        file_2 = tmp_path / "file_2"

        file_1.write_text("foo")
        file_2.write_text("foo")

        file_list = file_list_for_request([file_1, file_2], "foo")
        assert len(file_list) == 2
        assert all(len(member[1]) == 2 for member in file_list)

        file_list_2 = file_list_for_request([file_1, file_2], "foo", "foo_mimetype")
        assert len(file_list_2) == 2
        assert all(len(member[1]) == 3 for member in file_list_2)

    def test_schema_from_environs(self, monkeypatch):
        prefix = "NOTIFIERS"
        name = "ENV_TEST"
        env_data = {
            "string": "foo",
            "integer": "8",
            "float_": "1.1",
            "bool_": "true",
            "bytes": "baz",
        }
        for key, value in env_data.items():
            monkeypatch.setenv(f"{prefix}_{name}_{key}".upper(), value)

        data = dict_from_environs(prefix, name, list(env_data))
        assert TypeTest.parse_obj(data) == TypeTest(
            string="foo", integer=8, float_=1.1, bool_=True, bytes=b"baz"
        )
