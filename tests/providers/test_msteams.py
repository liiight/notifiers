import pytest

from notifiers.exceptions import NotificationError, BadArguments

provider = "msteams"


class TestMSTeams:
    """MS Teams tests"""

    @pytest.mark.parametrize(
        "data, missing", [
            ({"title": "foo", "webhook_url": "bar"}, "message"),
            ({"message": "foo"}, "webhook_url")
        ]
    )
    def test_msteams_missing_required(self, data, missing, provider):
        data["end_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{missing}' is a required property" in e.value.message