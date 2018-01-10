import pytest

import notifiers
from notifiers.core import Provider, Response
from notifiers.exceptions import BadArguments, SchemaError, NotificationError


class TestCore:
    """Test core classes"""
    valid_data = {'required': 'foo',
                  'not_required': ['foo', 'bar']}

    def test_sanity(self, mock_provider):
        """Test basic notification flow"""
        p = mock_provider()
        assert p.metadata == {'base_url': 'https://api.mock.com',
                              'provider_name': 'mock_provider',
                              'site_url': 'https://www.mock.com'}
        assert p.arguments == {
            'not_required': {
                'oneOf': [
                    {
                        'type': 'array', 'items': {
                        'type': 'string', 'title': 'example for not required arg'},
                        'minItems': 1,
                        'uniqueItems': True
                    },
                    {'type': 'string', 'title': 'example for not required arg'}
                ]
            },
            'required': {'type': 'string'}, 'option_with_default': {'type': 'string'},
            'message': {'type': 'string'}}

        assert p.required == {'required': ['required']}
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
        """Test correct schema validations"""
        p = mock_provider()

        with pytest.raises(BadArguments):
            p.notify(**data)

    def test_bad_schema(self, mock_provider):
        """Test illegal JSON schema"""
        p = mock_provider()
        p._schema = {'type': 'bad_schema'}
        data = {'foo': 'bar'}
        with pytest.raises(SchemaError):
            p.notify(**data)

    def test_prepare_data(self, mock_provider):
        """Test ``prepare_data()`` method"""
        p = mock_provider()
        rsp = p.notify(**self.valid_data)
        assert rsp.data == {'not_required': 'foo,bar',
                            'required': 'foo',
                            'option_with_default': 'foo'}

    def test_get_notifier(self, mock_provider):
        """Test ``get_notifier()`` helper function"""
        from notifiers import get_notifier
        p = get_notifier('mock')
        assert p
        assert isinstance(p, Provider)

    def test_all_providers(self, mock_provider, monkeypatch):
        """Test ``all_providers()`` helper function"""

        def mock_providers():
            return ['mock']

        monkeypatch.setattr(notifiers, 'all_providers', mock_providers)

        assert 'mock' in notifiers.all_providers()

    def test_error_response(self, mock_provider):
        """Test error notification response"""
        p = mock_provider()
        rsp = p.notify(**self.valid_data)
        rsp.errors = ['an error']
        rsp.status = 'fail'

        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert repr(e.value) == '<NotificationError: Notification errors: an error>'
        assert e.value.errors == ['an error']
        assert e.value.data == {'not_required': 'foo,bar', 'required': 'foo', 'option_with_default': 'foo'}
        assert e.value.message == 'Notification errors: an error'
        assert e.value.provider == p.provider_name

    def test_bad_integration(self, bad_provider):
        """Test bad provider inheritance"""
        p = bad_provider()
        with pytest.raises(NotImplementedError):
            p.notify(**self.valid_data)

    def test_environs(self, mock_provider, monkeypatch):
        """Test environs usage"""
        p = mock_provider()
        prefix = f'mock_'
        monkeypatch.setenv(f'{prefix}{p.provider_name}_required'.upper(), 'foo')
        rsp = p.notify(env_prefix=prefix)
        assert rsp.status == 'success'
        assert rsp.data['required'] == 'foo'

    def test_provided_data_takes_precedence_over_environ(self, mock_provider, monkeypatch):
        """Verify that given data overrides environ"""
        p = mock_provider()
        prefix = f'mock_'
        monkeypatch.setenv(f'{prefix}{p.provider_name}_required'.upper(), 'foo')
        rsp = p.notify(required='bar', env_prefix=prefix)
        assert rsp.status == 'success'
        assert rsp.data['required'] == 'bar'
