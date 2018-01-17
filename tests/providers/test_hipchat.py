import pytest

from notifiers.exceptions import BadArguments, NotificationError


class TestHipchat:
    # No online test for hipchat since they're deprecated and denies new signups
    provider = 'hipchat'

    def test_metadata(self, provider):
        assert provider.metadata == {
            'base_url': 'https://{group}.hipchat.com',
            'name': 'hipchat',
            'site_url': 'https://www.hipchat.com/docs/apiv2',
        }

    @pytest.mark.parametrize('data, message', [
        ({'id': 'foo', 'token': 'bar', 'message': 'boo', 'room': 'bla', 'user': 'gg'},
         "Only one of 'room' or 'user' is allowed"),
        ({'id': 'foo', 'token': 'bar', 'message': 'boo', 'room': 'bla', 'team_server': 'gg', 'group': 'gg'},
         "Only one 'group' or 'team_server' is allowed"),
    ])
    def test_missing_required(self, data, message, provider):
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert message in e.value.message

    def test_bad_request(self, provider):
        data = {
            'token': 'foo',
            'room': 'baz',
            'message': 'bar',
            'id': 'bla',
            'group': 'nada'
        }
        with pytest.raises(NotificationError) as e:
            rsp = provider.notify(**data)
            rsp.raise_on_errors()
        assert 'Invalid OAuth session' in e.value.message

    def test_hipchat_resources(self, provider):
        assert provider.resources
        assert len(provider.resources) == 2
        for resource in provider.resources:
            assert getattr(provider, resource)


class TestHipChatRooms:
    provider = 'hipchat'
    resource = 'rooms'

    def test_hipchat_rooms_attribs(self, resource):
        assert resource.schema == {
            'type': 'object',
            'properties': {
                'token': {
                    'type': 'string',
                    'title': 'User token'
                },
                'start': {'type': 'integer',
                          'title': 'Start index'},
                'max_results': {'type': 'integer',
                                'title': 'Max results in reply'},
                'group': {'type': 'string',
                          'title': 'Hipchat group name'},
                'team_server': {'type': 'string',
                                'title': 'Hipchat team server'},
                'private': {'type': 'boolean',
                            'title': 'Include private rooms'},
                'archived': {'type': 'boolean',
                             'title': 'Include archive rooms'}},
            'additionalProperties': False,
            'allOf': [
                {'required': ['token']}
                , {'oneOf': [{'required': ['group']},
                             {'required': ['team_server']}],
                   'error_oneOf': "Only one 'group' or 'team_server' is allowed"}
            ]
        }

        assert resource.required == {'allOf': [
            {'required': ['token']}
            , {'oneOf': [{'required': ['group']},
                         {'required': ['team_server']}],
               'error_oneOf': "Only one 'group' or 'team_server' is allowed"}]}
        assert resource.name == self.provider

    def test_hipchat_rooms_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix='foo')


class TestHipChatUserss:
    provider = 'hipchat'
    resource = 'users'

    def test_hipchat_users_attribs(self, resource):
        assert resource.schema == {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'title': 'User token'},
                'start': {'type': 'integer',
                          'title': 'Start index'},
                'max_results': {'type': 'integer',
                                'title': 'Max results in reply'},
                'group': {'type': 'string',
                          'title': 'Hipchat group name'},
                'team_server': {'type': 'string',
                                'title': 'Hipchat team server'},
                'guests': {
                    'type': 'boolean',
                    'title': 'Include active guest users in response. Otherwise, no guest users will be included'},
                'deleted': {'type': 'boolean',
                            'title': 'Include deleted users'}},
            'additionalProperties': False, 'allOf': [{'required': ['token']}, {
                'oneOf': [{'required': ['group']}, {'required': ['team_server']}],
                'error_oneOf': "Only one 'group' or 'team_server' is allowed"}]}

        assert resource.required == {'allOf': [
            {'required': ['token']}
            , {'oneOf': [{'required': ['group']},
                         {'required': ['team_server']}],
               'error_oneOf': "Only one 'group' or 'team_server' is allowed"}]}
        assert resource.name == self.provider

    def test_hipchat_users_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix='foo')


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
