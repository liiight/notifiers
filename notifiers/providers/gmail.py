from __future__ import annotations

from pydantic import Field

from ..models import Hostname, Port
from . import email


class GmailSchema(email.SMTPSchema):
    host: Hostname = Field("smtp.gmail.com", description="the host of the SMTP server")
    port: Port = Field(587, description="the port number to use")
    tls: bool = Field(True, description="should TLS be used")


class Gmail(email.SMTP):
    """Send email via Gmail"""

    site_url = "https://www.google.com/gmail/about/"
    base_url = "smtp.gmail.com"
    name = "gmail"

    schema_model = GmailSchema
