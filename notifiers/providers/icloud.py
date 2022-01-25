from . import email


class iCloud(email.SMTP):
    """Send email via iCloud"""

    _required = {"required": ["message", "from", "to", "username", "password"]}

    site_url = "https://www.icloud.com/mail"
    base_url = "smtp.mail.me.com"
    name = "icloud"

    @property
    def defaults(self) -> dict:
        data = super().defaults
        data["host"] = self.base_url
        data["port"] = 587
        data["tls"] = True
        return data
