from __future__ import annotations

import mimetypes
import smtplib
import socket
from email.message import EmailMessage
from email.utils import formatdate
from functools import cache
from pathlib import Path
from smtplib import SMTPAuthenticationError, SMTPSenderRefused, SMTPServerDisconnected

from pydantic import Field, model_validator

from ..core import Provider, Response
from ..models import Email, FilePath, Hostname, OneOrMore, Port, SchemaModel
from ..utils.helpers import list_to_commas

DEFAULT_SUBJECT = "New email from 'notifiers'!"
DEFAULT_SMTP_HOST = "localhost"


@cache
def default_from() -> str:
    """
    The default FROM address, ``notifiers@<this machine's fully qualified domain name>``.
    Computed on first use since the hostname lookup can be slow.
    """
    return f"notifiers@{socket.getfqdn()}"


class SMTPSchema(SchemaModel):
    message: str = Field(description="the content of the email message")
    subject: str = Field(DEFAULT_SUBJECT, description="the subject of the email message")
    to: OneOrMore[Email] = Field(description="one or more email addresses to use")
    cc: OneOrMore[Email] | None = Field(None, description="one or more email addresses to use")
    bcc: OneOrMore[Email] | None = Field(None, description="one or more email addresses to use")
    from_: Email = Field(default_factory=default_from, alias="from", description="the FROM address to use in the email")
    attachments: OneOrMore[FilePath] | None = Field(None, description="one or more attachments to use in the email")
    host: Hostname = Field(DEFAULT_SMTP_HOST, description="the host of the SMTP server")
    port: Port = Field(25, description="the port number to use")
    username: str | None = Field(None, description="username if relevant")
    password: str | None = Field(None, description="password if relevant")
    tls: bool = Field(False, description="should TLS be used")
    ssl: bool = Field(False, description="should SSL be used")
    html: bool = Field(False, description="should the email be parse as an HTML file")
    login: bool = Field(True, description="Trigger login to server")

    @model_validator(mode="after")
    def _check_credentials(self):
        self.require_dependencies({"username": ["password"], "password": ["username"]})
        return self


class SMTP(Provider):
    """Send emails via SMTP"""

    base_url = None
    site_url = "https://en.wikipedia.org/wiki/Email"
    name = "email"

    schema_model = SMTPSchema

    @staticmethod
    def _get_mimetype(attachment: Path) -> tuple[str, str]:
        """Taken from https://docs.python.org/3/library/email.examples.html"""
        ctype, encoding = mimetypes.guess_type(str(attachment))
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        return maintype, subtype

    def __init__(self):
        super().__init__()
        self.smtp_server = None
        self.configuration = None

    def _prepare_data(self, data: dict) -> dict:
        if isinstance(data["to"], list):
            data["to"] = list_to_commas(data["to"])
        if isinstance(data.get("attachments"), str):
            data["attachments"] = [data["attachments"]]
        return data

    @staticmethod
    def _build_email(data: dict) -> EmailMessage:
        email = EmailMessage()
        email["To"] = data["to"]
        if "cc" in data:
            email["CC"] = data.get("cc")
        if "bcc" in data:
            email["Bcc"] = data.get("bcc")
        email["From"] = data["from"]
        email["Subject"] = data["subject"]
        email["Date"] = formatdate(localtime=True)
        content_type = "html" if data["html"] else "plain"
        email.add_alternative(data["message"], subtype=content_type)
        return email

    def _add_attachments(self, attachments: list[str], email: EmailMessage):
        for attachment_ in attachments:
            attachment = Path(attachment_)
            maintype, subtype = self._get_mimetype(attachment)
            email.add_attachment(
                attachment.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=attachment.name,
            )

    def _connect_to_server(self, data: dict):
        smtp_server_cls = smtplib.SMTP_SSL if data["ssl"] else smtplib.SMTP
        self.smtp_server = smtp_server_cls(data["host"], data["port"])
        self.configuration = self._get_configuration(data)
        if data["tls"] and not data["ssl"]:
            self.smtp_server.ehlo()
            self.smtp_server.starttls()

        if data["login"] and data.get("username"):
            self.smtp_server.login(data["username"], data["password"])

    @staticmethod
    def _get_configuration(data: dict) -> tuple:
        return data["host"], data["port"], data.get("username")

    def _send_notification(self, data: dict) -> Response:
        errors = None
        try:
            configuration = self._get_configuration(data)
            if not self.configuration or not self.smtp_server or self.configuration != configuration:
                self._connect_to_server(data)
            email = self._build_email(data)
            if data.get("attachments"):
                self._add_attachments(data["attachments"], email)
            self.smtp_server.send_message(email)
        except (
            SMTPServerDisconnected,
            SMTPSenderRefused,
            OSError,
            SMTPAuthenticationError,
        ) as e:
            errors = [str(e)]
        return self.create_response(data, errors=errors)
