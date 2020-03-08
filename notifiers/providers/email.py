import getpass
import mimetypes
import smtplib
import socket
from email.message import EmailMessage
from email.utils import formatdate
from pathlib import Path
from smtplib import SMTPAuthenticationError
from smtplib import SMTPSenderRefused
from smtplib import SMTPServerDisconnected
from typing import List
from typing import Tuple

from pydantic import EmailStr
from pydantic import Field
from pydantic import FilePath
from pydantic import root_validator
from pydantic import validator

from ..models.provider import Provider
from ..models.provider import ResourceSchema
from ..models.response import Response


class SMTPSchema(ResourceSchema):
    """SMTP email schema"""

    message: str = Field(..., description="The content of the email message")
    subject: str = Field(
        "New email from 'notifiers'!", description="The subject of the email message"
    )
    to: ResourceSchema.one_or_more_of(EmailStr) = Field(
        ..., description="One or more email addresses to use"
    )
    from_: ResourceSchema.one_or_more_of(EmailStr) = Field(
        f"{getpass.getuser()}@{socket.getfqdn()}",
        description="One or more FROM addresses to use",
        alias="from",
        title="from",
    )
    attachments: ResourceSchema.one_or_more_of(FilePath) = Field(
        [], description="One or more attachments to use in the email"
    )
    host: str = Field("localhost", description="The host of the SMTP server")
    port: int = Field(25, gt=0, lte=65535, description="The port number to use")
    username: str = Field(None, description="Username if relevant")
    password: str = Field(None, description="Password if relevant")
    tls: bool = Field(False, description="Should TLS be used")
    ssl: bool = Field(False, description="Should SSL be used")
    html: bool = Field(False, description="Should the content be parsed as HTML")
    login: bool = Field(True, description="Should login be triggered to the server")

    @root_validator(pre=True)
    def username_password_check(cls, values):
        if "password" in values and "username" not in values:
            raise ValueError("Cannot set password without sending a username")
        return values

    @validator("attachments")
    def values_to_list(cls, v):
        return cls.to_list(v)

    @validator("to", "from_")
    def comma_separated(cls, v):
        return cls.to_comma_separated(v)

    @property
    def hash(self):
        """Returns a hash value of host, port and username to check if configuration changed"""
        return hash((self.host, self.port, self.username))


class SMTP(Provider):
    """Send emails via SMTP"""

    base_url = None
    site_url = "https://en.wikipedia.org/wiki/Email"
    name = "email"

    schema_model = SMTPSchema

    @staticmethod
    def _get_mimetype(attachment: Path) -> Tuple[str, str]:
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
        self.configuration_hash = None

    @staticmethod
    def _build_email(data: SMTPSchema) -> EmailMessage:
        email = EmailMessage()
        email["To"] = data.to
        email["From"] = data.from_
        email["Subject"] = data.subject
        email["Date"] = formatdate(localtime=True)
        content_type = "html" if data.html else "plain"
        email.add_alternative(data.message, subtype=content_type)
        return email

    def add_attachments_to_email(self, attachments: List[Path], email: EmailMessage):
        for attachment in attachments:
            maintype, subtype = self._get_mimetype(attachment)
            email.add_attachment(
                attachment.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=attachment.name,
            )

    def _connect_to_server(self, data: SMTPSchema):
        smtp_server_type = smtplib.SMTP_SSL if data.ssl else smtplib.SMTP
        self.smtp_server = smtp_server_type(data.host, data.port)
        self.configuration_hash = data.hash
        if data.tls and not data.ssl:
            self.smtp_server.ehlo()
            self.smtp_server.starttls()

        if data.login and data.username:
            self.smtp_server.login(data.username, data.password)

    def _send_notification(self, data: SMTPSchema) -> Response:
        errors = None
        connection_conditions = (
            not self.smtp_server,
            not self.configuration_hash,
            self.configuration_hash != data.hash,
        )
        try:
            if any(connection_conditions):
                self._connect_to_server(data)
            email = self._build_email(data)
            self.add_attachments_to_email(data.attachments, email)
            self.smtp_server.send_message(email)
        except (
            SMTPServerDisconnected,
            SMTPSenderRefused,
            socket.error,
            OSError,
            IOError,
            SMTPAuthenticationError,
        ) as e:
            errors = [str(e)]
        return self.create_response(data.dict(), errors=errors)
