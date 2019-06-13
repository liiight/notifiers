import pytest

from notifiers.exceptions import BadArguments, NotificationError, ResourceError

provider = "hipchat"


class TestHipchat:
    # No online test for hipchat since they're deprecated and denies new signups

    def test_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "https://{group}.hipchat.com",
            "name": "hipchat",
            "site_url": "https://www.hipchat.com/docs/apiv2",
        }

    @pytest.mark.parametrize(
        "data, message",
        [
            (
                {
                    "id": "foo",
                    "token": "bar",
                    "message": "boo",
                    "room": "bla",
                    "user": "gg",
                },
                "Only one of 'room' or 'user' is allowed",
            ),
            (
                {
                    "id": "foo",
                    "token": "bar",
                    "message": "boo",
                    "room": "bla",
                    "team_server": "gg",
                    "group": "gg",
                },
                "Only one 'group' or 'team_server' is allowed",
            ),
        ],
    )
    def test_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert message in e.value.message

    def test_bad_request(self, provider):
        data = {
            "token": "foo",
            "room": "baz",
            "message": "bar",
            "id": "bla",
            "group": "nada",
        }
        with pytest.raises(NotificationError) as e:
            provider.notify(**data, raise_on_errors=True)
        assert "Failed to establish a new connection" in e.value.message

    def test_hipchat_resources(self, provider):
        assert provider.resources
        assert len(provider.resources) == 2
        for resource in provider.resources:
            assert getattr(provider, resource)


class TestHipChatRooms:
    resource = "rooms"

    def test_hipchat_rooms_attribs(self, resource):
        assert resource.schema == {
            "type": "object",
            "properties": {
                "token": {"type": "string", "title": "User token"},
                "start": {"type": "integer", "title": "Start index"},
                "max_results": {"type": "integer", "title": "Max results in reply"},
                "group": {"type": "string", "title": "Hipchat group name"},
                "team_server": {"type": "string", "title": "Hipchat team server"},
                "private": {"type": "boolean", "title": "Include private rooms"},
                "archived": {"type": "boolean", "title": "Include archive rooms"},
            },
            "additionalProperties": False,
            "allOf": [
                {"required": ["token"]},
                {
                    "oneOf": [{"required": ["group"]}, {"required": ["team_server"]}],
                    "error_oneOf": "Only one 'group' or 'team_server' is allowed",
                },
            ],
        }

        assert resource.required == {
            "allOf": [
                {"required": ["token"]},
                {
                    "oneOf": [{"required": ["group"]}, {"required": ["team_server"]}],
                    "error_oneOf": "Only one 'group' or 'team_server' is allowed",
                },
            ]
        }
        assert resource.name == provider

    def test_hipchat_rooms_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix="foo")

    def test_hipchat_rooms_negative_2(self, resource):
        with pytest.raises(ResourceError) as e:
            resource(token="foo", group="bat")

        assert 'Failed to establish a new connection' in e.value.errors[0]


class TestHipChatUsers:
    resource = "users"

    def test_hipchat_users_attribs(self, resource):
        assert resource.schema == {
            "type": "object",
            "properties": {
                "token": {"type": "string", "title": "User token"},
                "start": {"type": "integer", "title": "Start index"},
                "max_results": {"type": "integer", "title": "Max results in reply"},
                "group": {"type": "string", "title": "Hipchat group name"},
                "team_server": {"type": "string", "title": "Hipchat team server"},
                "guests": {
                    "type": "boolean",
                    "title": "Include active guest users in response. Otherwise, no guest users will be included",
                },
                "deleted": {"type": "boolean", "title": "Include deleted users"},
            },
            "additionalProperties": False,
            "allOf": [
                {"required": ["token"]},
                {
                    "oneOf": [{"required": ["group"]}, {"required": ["team_server"]}],
                    "error_oneOf": "Only one 'group' or 'team_server' is allowed",
                },
            ],
        }

        assert resource.required == {
            "allOf": [
                {"required": ["token"]},
                {
                    "oneOf": [{"required": ["group"]}, {"required": ["team_server"]}],
                    "error_oneOf": "Only one 'group' or 'team_server' is allowed",
                },
            ]
        }
        assert resource.name == provider

    def test_hipchat_users_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix="foo")


class TestHipchatCLI:
    """Test hipchat specific CLI"""

    def test_hipchat_rooms_negative(self, cli_runner):
        cmd = "hipchat rooms --token bad_token".split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output

    def test_hipchat_users_negative(self, cli_runner):
        cmd = "hipchat users --token bad_token".split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert not result.output
