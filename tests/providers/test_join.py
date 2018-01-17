import pytest

from notifiers.exceptions import BadArguments, ResourceError

provider = 'join'


class TestJoin:

    def test_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1',
            'name': 'join',
            'site_url': 'https://joaoapps.com/join/api/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'apikey'),
        ({'apikey': 'foo'}, 'message'),
    ])
    def test_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    def test_defaults(self, provider):
        assert provider.defaults == {'deviceId': 'group.all'}

    @pytest.mark.skip('tests fail due to no device connected')
    @pytest.mark.online
    def test_sanity(self, provider):
        data = {'message': 'foo'}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()


class TestJoinDevices:
    resource = 'devices'

    def test_join_devices_attribs(self, resource):
        assert resource.schema == {
            'type': 'object',
            'properties': {
                'apikey': {'type': 'string', 'title': 'user API key'}},
            'additionalProperties': False,
            'required': ['apikey']
        }

    def test_join_devices_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix='foo')

    def test_join_negative(self, resource):
        with pytest.raises(ResourceError) as e:
            resource(apikey='foo')
        assert e.value.errors == ['Not Found']
        assert e.value.response.status_code == 404


@pytest.mark.skip('Provider resources CLI command are not ready yet')
class TestJoinCLI:
    """Test Join specific CLI"""

    def test_join_devices_negative(self, cli_runner):
        cmd = 'join devices --token bad_token'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output

    @pytest.mark.skip('tests fail due to no device connected')
    @pytest.mark.online
    def test_join_updates_positive(self, cli_runner):
        cmd = f'join devices'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        replies = ['You have no devices associated with this apikey', 'Device name: ']
        assert any(reply in result.output for reply in replies)
