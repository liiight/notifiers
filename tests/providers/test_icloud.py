import pytest
from notifiers.exceptions import BadArguments, NotificationError

provider = "icloud"


class TestiCloud:
    """iCloud tests"""

    def test_icloud_metadata(self, provider):
        assert provider.metadata == {
            "base_url": "smtp.mail.me.com",
            "name": "icloud",
            "site_url": "https://www.icloud.com/mail",
        }

    @pytest.mark.parametrize("data, message", [({}, "message"), ({"message": "foo"}, "to")])
    def test_icloud_missing_required(self, data, message, provider):
        data["env_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
            print(e.value.message)
        assert f"'{message}' is a required property" in e.value.message

    @pytest.mark.online
    def test_smtp_sanity(self, provider, test_message):
        """using iCloud SMTP"""
        data = {
            "message": f"<b>{test_message}</b>",
            "html": True,
            "tls": True,
            "port": 587,
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_email_from_key(self, provider):
        rsp = provider.notify(
            to="foo@foo.com",
            from_="bla@foo.com",
            message="foo",
            host="goo",
            username="ding",
            password="dong",
        )
        rsp_data = rsp.data
        assert not rsp_data.get("from_")
        assert rsp_data["from"] == "bla@foo.com"

    def test_multiple_to(self, provider):
        to = ["foo@foo.com", "bar@foo.com"]
        rsp = provider.notify(to=to, message="foo", host="goo", username="ding", password="dong")
        assert rsp.data["to"] == ",".join(to)

    def test_icloud_negative(self, provider):
        data = {
            "username": "foo",
            "password": "foo",
            "from": "bla@foo.com",
            "to": "foo@foo.com",
            "message": "bar",
        }
        rsp = provider.notify(**data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert "5.7.8 Error: authentication failed" in e.value.errors[0]
