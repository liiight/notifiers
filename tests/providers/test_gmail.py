import pytest

from notifiers.exceptions import NotificationError

provider = "gmail"


class TestGmail:
    """Gmail tests"""

    @pytest.mark.online
    def test_smtp_sanity(self, provider, test_message):
        """using Gmail SMTP"""
        data = {
            "message": f"<b>{test_message}</b>",
            "html": True,
            "ssl": True,
            "port": 465,
        }
        rsp = provider.notify(**data)
        rsp.raise_on_errors()

    def test_multiple_to(self, provider):
        to = ["foo@foo.com", "bar@foo.com"]
        rsp = provider.notify(
            to=to, message="foo", host="goo", username="ding", password="dong"
        )
        assert rsp.data["to"] == ",".join(to)

    def test_gmail_negative(self, provider):
        data = {
            "username": "foo",
            "password": "foo",
            "to": "foo@foo.com",
            "message": "bar",
        }
        rsp = provider.notify(**data)
        with pytest.raises(NotificationError) as e:
            rsp.raise_on_errors()

        assert "Username and Password not accepted" in e.value.errors[0]
