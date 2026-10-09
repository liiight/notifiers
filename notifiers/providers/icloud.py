from __future__ import annotations

from pydantic import Field

from ..models import Hostname, Port
from . import email


class iCloudSchema(email.SMTPSchema):
    # iCloud only accepts mail from the account's own address, the default is just a fallback
    required_with_default = frozenset({"from_"})

    username: str = Field(description="username if relevant")
    password: str = Field(description="password if relevant")
    host: Hostname = Field("smtp.mail.me.com", description="the host of the SMTP server")
    port: Port = Field(587, description="the port number to use")
    tls: bool = Field(True, description="should TLS be used")


class iCloud(email.SMTP):
    """Send email via iCloud"""

    site_url = "https://www.icloud.com/mail"
    base_url = "smtp.mail.me.com"
    name = "icloud"

    schema_model = iCloudSchema
