from pydantic import Field

from . import email

GMAIL_SMTP_HOST = "smtp.gmail.com"


class GmailSchema(email.SMTPSchema):
    host: str = Field(GMAIL_SMTP_HOST, description="The host of the SMTP server")
    port: int = Field(587, gt=0, lte=65535, description="The port number to use")
    tls: bool = Field(True, description="Should TLS be used")


class Gmail(email.SMTP):
    """Send email via Gmail"""

    site_url = "https://www.google.com/gmail/about/"
    base_url = GMAIL_SMTP_HOST
    name = "gmail"
    schema_model = GmailSchema
