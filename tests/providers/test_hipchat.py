import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestHipchat:
    # No online tess for hipchat since they're deprecated and denies new signups
    notifier_name = 'hipchat'

    def test_metadata(self):
        p = get_notifier(self.notifier_name)
        assert p.metadata == {
            'base_url': 'https://{group}.hipchat.com',
            'provider_name': 'hipchat',
            'room_url': '/v2/room/{room}/notification',
            'site_url': 'https://www.hipchat.com/docs/apiv2',
            'user_url': '/v2/user/{user}/message'
        }

    @pytest.mark.parametrize('data, message', [
        ({'id': 'foo', 'token': 'bar', 'message': 'boo', 'room': 'bla', 'user': 'gg'},
         "Only one of 'room' or 'user' is allowed"),
        ({'id': 'foo', 'token': 'bar', 'message': 'boo', 'room': 'bla', 'team_server': 'gg', 'group': 'gg'},
         "Only one 'group' or 'team_server' is allowed"),
    ])
    def test_missing_required(self, data, message):
        p = get_notifier(self.notifier_name)
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert message in e.value.message

    def test_bad_request(self):
        p = get_notifier(self.notifier_name)
        data = {
            'token': 'foo',
            'room': 'baz',
            'message': 'bar',
            'id': 'bla',
            'group': 'nada'
        }
        with pytest.raises(NotificationError) as e:
            rsp = p.notify(**data)
            rsp.raise_on_errors()
        assert 'Invalid OAuth session' in e.value.message


@pytest.mark.skip('Provider resources CLI command are not ready yet')
class TestHipchatCLI:
    """Test hipchat specific CLI"""

    def test_hipchat_rooms_negative(self, cli_runner):
        cmd = 'hipchat rooms --token bad_token'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output

    def test_hipchat_users_negative(self, cli_runner):
        cmd = 'hipchat users --token bad_token'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output
