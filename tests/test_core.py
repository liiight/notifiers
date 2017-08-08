import pytest

from notifiers.core import NotificationProvider, NotificationResponse
from notifiers.exceptions import BadArguments, SchemaError, NotificationError


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
        assert repr(rsp) == '<NotificationResponse,provider=Mock_provider,status=success>'
        assert repr(p) == '<NotificationProvider:[Mock_provider]>'

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

    def test_get_notifier(self, mock_provider):
        from notifiers import get_notifier
        p = get_notifier('mock')
        assert p
        assert isinstance(p, NotificationProvider)

    def test_all_providers(self, mock_provider):
        from notifiers import all_providers
        assert 'mock' in all_providers()

    def test_error_response(self, mock_provider):
        p = mock_provider()
        rsp = p.notify(**self.valid_data)
        rsp.errors = ['an error']
        rsp.status = 'fail'

        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert repr(e.value) == '<NotificationError: Notification errors: an error>'
        assert e.value.errors == ['an error']
        assert e.value.data == {'not_required': 'foo,bar', 'required': 'foo'}
        assert e.value.message == 'Notification errors: an error'
        assert e.value.provider == p.provider_name

    def test_bad_integration(self, bad_provider):
        p = bad_provider()
        with pytest.raises(NotImplementedError):
            p.notify(**self.valid_data)

    def test_environs(self, mock_provider, set_environs):
        p = mock_provider()
        prefix = f'mock_'
        environs = {
            f'{prefix}{p.provider_name}_required': 'foo'
        }
        set_environs(**environs)
        rsp = p.notify(env_prefix=prefix)
        assert rsp.status == 'success'
