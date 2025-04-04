import pytest

from notifiers.exceptions import BadArguments, NotificationError, ResourceError

provider = "gitter"


class TestGitter:
    def test_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "https://api.gitter.im/v1/rooms",
            "message_url": "/{room_id}/chatMessages",
            "name": "gitter",
            "site_url": "https://gitter.im",
        }

    @pytest.mark.parametrize(
        ("data", "message"),
        [
            ({}, "message"),
            ({"message": "foo"}, "token"),
            ({"message": "foo", "token": "bar"}, "room_id"),
        ],
    )
    def test_missing_required(self, provider, data, message):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.skip(reason="Disabled account")
    @pytest.mark.online
    def test_bad_request(self, provider):
        data = {"token": "foo", "room_id": "baz", "message": "bar"}
        with pytest.raises(NotificationError) as e:
            provider.notify(**data).raise_on_errors()

        assert "Unauthorized" in e.value.message

    @pytest.mark.online
    @pytest.mark.skip(reason="Disabled account")
    def test_bad_room_id(self, provider):
        data = {"room_id": "baz", "message": "bar"}
        with pytest.raises(NotificationError) as e:
            provider.notify(**data).raise_on_errors()

        assert "Bad Request" in e.value.message

    @pytest.mark.online
    @pytest.mark.skip(reason="Disabled account")
    def test_sanity(self, provider, test_message):
        data = {"message": test_message}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_gitter_resources(self, provider):
        assert provider.resources
        for resource in provider.resources:
            assert getattr(provider, resource)
        assert "rooms" in provider.resources


@pytest.mark.skip(reason="Disabled account")
class TestGitterResources:
    resource = "rooms"

    def test_gitter_rooms_attribs(self, resource):
        assert resource.schema == {
            "type": "object",
            "properties": {
                "token": {"type": "string", "title": "access token"},
                "filter": {"type": "string", "title": "Filter results"},
            },
            "required": ["token"],
            "additionalProperties": False,
        }
        assert resource.name == provider
        assert resource.required == {"required": ["token"]}

    def test_gitter_rooms_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix="foo")

    def test_gitter_rooms_negative_2(self, resource):
        with pytest.raises(ResourceError) as e:
            resource(token="foo")
        assert e.value.errors == ["Unauthorized"]
        assert e.value.response.status_code == 401

    @pytest.mark.online
    def test_gitter_rooms_positive(self, resource):
        rsp = resource()
        assert isinstance(rsp, list)

    @pytest.mark.online
    def test_gitter_rooms_positive_with_filter(self, resource):
        assert resource(filter="notifiers/testing")


@pytest.mark.skip(reason="Disabled account")
class TestGitterCLI:
    """Test Gitter specific CLI commands"""

    def test_gitter_rooms_negative(self, cli_runner):
        cmd = ["gitter", "rooms", "--token", "bad_token"]
        result = cli_runner(cmd)
        assert result.exit_code
        assert not result.output

    @pytest.mark.online
    def test_gitter_rooms_positive(self, cli_runner):
        cmd = ["gitter", "rooms"]
        result = cli_runner(cmd)
        assert not result.exit_code
        assert "notifiers/testing" in result.output

    @pytest.mark.online
    def test_gitter_rooms_with_query(self, cli_runner):
        cmd = ["gitter", "rooms", "--filter", "notifiers/testing"]
        result = cli_runner(cmd)
        assert not result.exit_code
        assert "notifiers/testing" in result.output
