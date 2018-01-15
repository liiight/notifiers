import os

import pytest

from notifiers import get_notifier
from notifiers.exceptions import BadArguments, NotificationError


class TestGitter:
    def test_metadata(self):
        p = get_notifier('gitter')
        assert p.metadata == {
            'base_url': 'https://api.gitter.im/v1/rooms',
            'message_url': 'https://api.gitter.im/v1/rooms/{room_id}/chatMessages',
            'name': 'gitter',
            'site_url': 'https://gitter.im'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'message'),
        ({'message': 'foo'}, 'token'),
        ({'message': 'foo', 'token': 'bar'}, 'room_id'),
    ])
    def test_missing_required(self, data, message):
        p = get_notifier('gitter')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    def test_bad_request(self):
        p = get_notifier('gitter')
        data = {
            'token': 'foo',
            'room_id': 'baz',
            'message': 'bar'
        }
        with pytest.raises(NotificationError) as e:
            rsp = p.notify(**data)
            rsp.raise_on_errors()
        assert 'Unauthorized' in e.value.message

    @pytest.mark.online
    def test_bad_room_id(self):
        p = get_notifier('gitter')
        data = {
            'room_id': 'baz',
            'message': 'bar'
        }
        with pytest.raises(NotificationError) as e:
            rsp = p.notify(**data)
            rsp.raise_on_errors()
        assert 'Bad Request' in e.value.message

    @pytest.mark.online
    def test_sanity(self):
        p = get_notifier('gitter')
        data = {
            'message': 'bar'
        }
        rsp = p.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_gitter_rooms(self):
        p = get_notifier('gitter')
        assert p.rooms()


@pytest.mark.skip('Provider resources CLI command are not ready yet')
class TestGitterCLI:
    """Test Gitter specific CLI commands"""

    def test_gitter_rooms_negative(self, cli_runner):
        cmd = 'gitter rooms --token bad_token'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output

    @pytest.mark.online
    def test_gitter_rooms_positive(self, cli_runner):
        cmd = 'gitter rooms'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert 'notifiers/testing' in result.output

    @pytest.mark.online
    def test_gitter_rooms_with_query(self, cli_runner):
        cmd = f'gitter rooms --filter notifiers/testing'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert 'notifiers/testing' in result.output
