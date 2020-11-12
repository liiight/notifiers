from hypothesis import given
from hypothesis import strategies as st

from notifiers.models.schema import ResourceSchema

simple_type = st.one_of(st.text(), st.dates(), st.booleans())

given_any_object = given(
    st.one_of(
        simple_type,
        st.dictionaries(keys=simple_type, values=simple_type),
        st.lists(elements=simple_type),
    )
)


class TestResourceSchema:
    """Test the resource schema base class"""

    @given_any_object
    def test_to_list(self, any_object):
        list_of_obj = [any_object] if not isinstance(any_object, list) else any_object
        assert ResourceSchema.to_list(any_object) == list_of_obj

    @given_any_object
    def test_to_csv(self, any_object):
        list_of_obj = ResourceSchema.to_list(any_object)
        assert ResourceSchema.to_comma_separated(any_object) == ",".join(
            str(value) for value in list_of_obj
        )

    def test_to_dict(self, mock_provider):
        data = {"required": "foo"}
        mock = mock_provider.validate_data(data)
        assert mock.to_dict() == {"option_with_default": "foo", "required": "foo"}
