import pytest

from notifiers.exceptions import BadArguments

provider = "simplepush"


class TestSimplePush:
    """SimplePush notifier tests

    Note: These tests assume correct environs set for NOTIFIERS_SIMPLEPUSH_KEY
    """

    @pytest.mark.parametrize(
        "data, message", [({}, "key"), ({"key": "foo"}, "message")]
    )
    def test_simplepush_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_simplepush_sanity(self, provider, test_message):
        """Successful simplepush notification"""
        data = {"message": test_message}
        rsp = provider.notify(**data)
        rsp.raise_on_errors()
