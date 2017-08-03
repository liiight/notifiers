import pytest

from notifiers.core import NotificationProvider, NotificationResponse
from notifiers.exceptions import BadArguments, SchemaError
from notifiers.utils.json_schema import one_or_more, list_to_commas


@pytest.fixture
def mock_provider() -> NotificationProvider:
    class MockProvider(NotificationProvider):
        base_url = 'https://api.mock.com'
        schema = {
            'type': 'object',
            'properties': {
                'not_required': one_or_more({'type': 'string'}),
                'required': {'type': 'string'}
            },
            'required': ['required'],
            'additionalProperties': False
        }
        site_url = 'https://www.mock.com'
        provider_name = 'mock_provider'

        def _send_notification(self, data: dict):
            return NotificationResponse(status='success', provider=self.provider_name, data=data)

        def _prepare_data(self, data: dict):
            if data.get('not_required'):
                data['not_required'] = list_to_commas(data['not_required'])
            return data

    return MockProvider


class TestCore(object):
    """Test core classes"""
    valid_data = {'required': 'foo',
                  'not_required': ['foo', 'bar']}

    def test_sanity(self, mock_provider):
        p = mock_provider()
        assert p.metadata == {'base_url': 'https://api.mock.com',
                              'provider_name': 'mock_provider',
                              'site_url': 'https://www.mock.com'}
        assert p.arguments == {
            'not_required': {
                'oneOf': [
                    {'items': {'type': 'string'}, 'minItems': 1, 'type': 'array', 'uniqueItems': True},
                    {'type': 'string'}
                ]
            },
            'required': {'type': 'string'}
        }

        assert p.required == ['required']
        rsp = p.notify(**self.valid_data)
        assert isinstance(rsp, NotificationResponse)
        assert not rsp.errors
        assert rsp.raise_on_errors() is None

    @pytest.mark.parametrize('data', [
        pytest.param({'not_required': 'foo'}, id='Missing required'),
        pytest.param({'required': 6}, id='Wrong type'),
        pytest.param({'foo': 6}, id='Additional properties not allowed'),
    ])
    def test_schema_validation(self, data, mock_provider):
        p = mock_provider()

        with pytest.raises(BadArguments):
            p.notify(**data)

    def test_bad_schema(self, mock_provider):
        p = mock_provider()
        p.schema = {'type': 'bad_schema'}
        data = {'foo': 'bar'}
        with pytest.raises(SchemaError):
            p.notify(**data)

    def test_prepare_data(self, mock_provider):
        p = mock_provider()
        rsp = p.notify(**self.valid_data)
        assert rsp.data == {'not_required': 'foo,bar',
                            'required': 'foo'}
