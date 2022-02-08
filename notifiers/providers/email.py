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

from ..core import Provider
from ..core import Response
from ..utils.schema.helpers import list_to_commas
from ..utils.schema.helpers import one_or_more

DEFAULT_SUBJECT = "New email from 'notifiers'!"
DEFAULT_FROM = f"notifiers@{socket.getfqdn()}"
DEFAULT_SMTP_HOST = "localhost"


class SMTP(Provider):
    """Send emails via SMTP"""

    base_url = None
    site_url = "https://en.wikipedia.org/wiki/Email"
    name = "email"

    _required = {"required": ["message", "to"]}

    _schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "title": "the content of the email message"},
            "subject": {"type": "string", "title": "the subject of the email message"},
            "to": one_or_more(
                {
                    "type": "string",
                    "format": "email",
                    "title": "one or more email addresses to use",
                }
            ),
            "from": {
                "type": "string",
                "format": "email",
                "title": "the FROM address to use in the email",
            },
            "from_": {
                "type": "string",
                "format": "email",
                "title": "the FROM address to use in the email",
                "duplicate": True,
            },
            "attachments": one_or_more(
                {
                    "type": "string",
                    "format": "valid_file",
                    "title": "one or more attachments to use in the email",
                }
            ),
            "host": {
                "type": "string",
                "format": "hostname",
                "title": "the host of the SMTP server",
            },
            "port": {
                "type": "integer",
                "format": "port",
                "title": "the port number to use",
            },
            "username": {"type": "string", "title": "username if relevant"},
            "password": {"type": "string", "title": "password if relevant"},
            "tls": {"type": "boolean", "title": "should TLS be used"},
            "ssl": {"type": "boolean", "title": "should SSL be used"},
            "html": {
                "type": "boolean",
                "title": "should the email be parse as an HTML file",
            },
            "login": {"type": "boolean", "title": "Trigger login to server"},
        },
        "dependencies": {
            "username": ["password"],
            "password": ["username"],
            "ssl": ["tls"],
        },
        "additionalProperties": False,
    }

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
        self.configuration = None

    @property
    def defaults(self) -> dict:
        return {
            "subject": DEFAULT_SUBJECT,
            "from": DEFAULT_FROM,
            "host": DEFAULT_SMTP_HOST,
            "port": 25,
            "tls": False,
            "ssl": False,
            "html": False,
            "login": True,
        }

    def _prepare_data(self, data: dict) -> dict:
        if isinstance(data["to"], list):
            data["to"] = list_to_commas(data["to"])
        # A workaround since `from` is a reserved word
        if data.get("from_"):
            data["from"] = data.pop("from_")
        return data

    @staticmethod
    def _build_email(data: dict) -> EmailMessage:
        email = EmailMessage()
        email["To"] = data["to"]
        email["From"] = data["from"]
        email["Subject"] = data["subject"]
        email["Date"] = formatdate(localtime=True)
        content_type = "html" if data["html"] else "plain"
        email.add_alternative(data["message"], subtype=content_type)
        return email

    def _add_attachments(self, attachments: List[str], email: EmailMessage):
        for attachment in attachments:
            attachment = Path(attachment)
            maintype, subtype = self._get_mimetype(attachment)
            email.add_attachment(
                attachment.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=attachment.name,
            )

    def _connect_to_server(self, data: dict):
        self.smtp_server = smtplib.SMTP_SSL if data["ssl"] else smtplib.SMTP
        self.smtp_server = self.smtp_server(data["host"], data["port"])
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
            if (
                not self.configuration
                or not self.smtp_server
                or self.configuration != configuration
            ):
                self._connect_to_server(data)
            email = self._build_email(data)
            if data.get("attachments"):
                self._add_attachments(data["attachments"], email)
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
        return self.create_response(data, errors=errors)
