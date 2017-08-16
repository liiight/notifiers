import pytest

import notifiers
from notifiers.core import Provider, Response
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
        assert isinstance(rsp, Response)
        assert not rsp.errors
        assert rsp.raise_on_errors() is None
        assert repr(rsp) == '<Response,provider=Mock_provider,status=success>'
        assert repr(p) == '<Provider:[Mock_provider]>'

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
        assert isinstance(p, Provider)

    def test_all_providers(self, mock_provider, monkeypatch):
        def mock_providers():
            return ['mock']

        monkeypatch.setattr(notifiers, 'all_providers', mock_providers)

        assert 'mock' in notifiers.all_providers()

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

    def test_environs(self, mock_provider, monkeypatch):
        p = mock_provider()
        prefix = f'mock_'
        monkeypatch.setenv(f'{prefix}{p.provider_name}_required', 'foo')
        rsp = p.notify(env_prefix=prefix)
        assert rsp.status == 'success'
        assert rsp.data['required'] == 'foo'
