import pytest

from notifiers.exceptions import BadArguments
from notifiers.exceptions import NotificationError

provider = "pushover"


class TestPushover:
    """Pushover notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_PUSHOVER_TOKEN and NOTIFIERS_PUSHOVER_USER
    """

    @pytest.mark.parametrize(
        "data, message",
        [
            ({}, "user"),
            ({"user": "foo"}, "message"),
            ({"user": "foo", "message": "bla"}, "token"),
        ],
    )
    def test_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.parametrize(
        "data, message", [({}, "expire"), ({"expire": 30}, "retry")]
    )
    @pytest.mark.online
    def test_pushover_priority_2_restrictions(
        self, data, message, provider, test_message
    ):
        """Pushover specific API restrictions when using priority 2"""
        base_data = {"message": test_message, "priority": 2}
        final_data = {**base_data, **data}
        rsp = provider.notify(**final_data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()
        assert message in e.value.message

    @pytest.mark.online
    def test_sanity(self, provider):
        """Successful pushover notification"""
        data = {"message": "foo"}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    @pytest.mark.online
    def test_all_options(self, provider, test_message):
        """Use all available pushover options"""
        data = {
            "message": test_message,
            "title": "title",
            "priority": 2,
            "url": "http://foo.com",
            "url_title": "url title",
            "sound": "bike",
            "timestamp": "0",
            "retry": 30,
            "expire": 30,
            "callback": "http://callback.com",
            "html": True,
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_attachment_negative(self, provider):
        data = {
            "token": "foo",
            "user": "bar",
            "message": "baz",
            "attachment": "/foo/bar.jpg",
        }
        with pytest.raises(BadArguments):
            provider.notify(**data)

    @pytest.mark.online
    def test_attachment_positive(self, provider, tmpdir):
        p = tmpdir.mkdir("test").join("image.jpg")
        p.write("im binary")
        data = {"attachment": p.strpath, "message": "foo"}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()


class TestPushoverSoundsResource:
    resource = "sounds"

    def test_pushover_sounds_attribs(self, resource):
        assert resource.schema == {
            "type": "object",
            "properties": {
                "token": {"type": "string", "title": "your application's API token"}
            },
            "required": ["token"],
        }

        assert resource.name == provider

    def test_pushover_sounds_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix="foo")

    @pytest.mark.online
    def test_pushover_sounds_positive(self, resource):
        assert isinstance(resource(), list)


class TestPushoverLimitsResource:
    resource = "limits"

    def test_pushover_limits_attribs(self, resource):
        assert resource.schema == {
            "type": "object",
            "properties": {
                "token": {"type": "string", "title": "your application's API token"}
            },
            "required": ["token"],
        }

        assert resource.name == provider

    def test_pushover_limits_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix="foo")

    @pytest.mark.online
    def test_pushover_limits_positive(self, resource):
        assert isinstance(resource(), dict)
        assert all(key in resource() for key in ["limit", "remaining", "reset"])


class TestPushoverCLI:
    def test_pushover_sounds_negative(self, cli_runner):
        cmd = "pushover sounds --token bad_token".split()
        result = cli_runner(cmd)
        assert result.exit_code
        assert not result.output

    @pytest.mark.online
    def test_pushover_sounds_positive(self, cli_runner):
        cmd = "pushover sounds".split()
        result = cli_runner(cmd)
        assert not result.exit_code
        assert "piano" in result.output

    def test_pushover_limits(self, cli_runner):
        cmd = "pushover limits --token bad_token".split()
        result = cli_runner(cmd)
        assert result.exit_code
        assert not result.output

    @pytest.mark.online
    def test_pushover_limits_positive(self, cli_runner):
        cmd = "pushover limits".split()
        result = cli_runner(cmd)
        assert not result.exit_code
        assert all(key in result.output for key in ["limit", "remaining", "reset"])
