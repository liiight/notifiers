import getpass
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTPAuthenticationError, SMTPServerDisconnected, SMTPSenderRefused

from ..core import Provider, Response
from ..utils.json_schema import one_or_more, list_to_commas

DEFAULT_SUBJECT = "New email from 'notifiers'!"
DEFAULT_FROM = f'{getpass.getuser()}@{socket.getfqdn()}'
DEFAULT_SMTP_HOST = 'localhost'


class SMTP(Provider):
    """Send emails via SMTP"""
    base_url = None
    site_url = 'https://en.wikipedia.org/wiki/Email'
    name = 'email'

    _required = {
        'required': ['message', 'to'],
        'dependencies': {
            'username': ['password'],
            'password': ['username'],
            'ssl': ['tls']
        }
    }

    _schema = {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'title': 'the content of the email message'
            },
            'subject': {
                'type': 'string',
                'title': 'the subject of the email message'
            },
            'to': one_or_more({
                'type': 'string',
                'format': 'email',
                'title': 'one or more email addresses to use'
            }),
            'from': {
                'type': 'string',
                'title': 'the FROM address to use in the email'
            },
            'from_': {
                'type': 'string',
                'title': 'the FROM address to use in the email',
                'duplicate': True
            },
            'host': {
                'type': 'string',
                'title': 'the host of the SMTP server'
            },
            'port': {
                'type': 'integer',
                'title': 'the port number to use'
            },
            'username': {
                'type': 'string',
                'title': 'username if relevant'
            },
            'password': {
                'type': 'string',
                'title': 'password if relevant'
            },
            'tls': {
                'type': 'boolean',
                'title': 'should TLS be used'
            },
            'ssl': {
                'type': 'boolean',
                'title': 'should SSL be used'
            },
            'html': {
                'type': 'boolean',
                'title': 'should the email be parse as an HTML file'
            }
        },
        'additionalProperties': False,
    }

    def __init__(self):
        super().__init__()
        self.smtp_server = None
        self.configuration = None

    @property
    def defaults(self) -> dict:
        return {
            'subject': DEFAULT_SUBJECT,
            'from': DEFAULT_FROM,
            'host': DEFAULT_SMTP_HOST,
            'port': 25,
            'tls': False,
            'ssl': False,
            'html': False
        }

    def _prepare_data(self, data: dict) -> dict:
        if isinstance(data['to'], list):
            data['to'] = list_to_commas(data['to'])
        # A workaround since `from` is a reserved word
        if data.get('from_'):
            data['from'] = data.pop('from_')
        return data

    def _build_email(self, data: dict) -> MIMEMultipart:
        email = MIMEMultipart('alternative')
        email['To'] = data['to']
        email['From'] = data['from']
        email['Subject'] = data['subject']
        email['Date'] = formatdate(localtime=True)
        content_type = 'html' if data['html'] else 'plain'
        email.attach(MIMEText(data['message'].encode('utf-8'), content_type, _charset='utf-8'))
        return email

    def _connect_to_server(self, data: dict):
        self.smtp_server = smtplib.SMTP_SSL if data['ssl'] else smtplib.SMTP
        self.smtp_server = self.smtp_server(data['host'], data['port'])
        self.configuration = self._get_configuration(data)
        if data['tls']:
            self.smtp_server.ehlo()
            self.smtp_server.starttls()
            self.smtp_server.ehlo()

        if data.get('username'):
            self.smtp_server.login(data['username'], data['password'])

    def _get_configuration(self, data: dict) -> tuple:
        return data['host'], data['port'], data.get('username')

    def _send_notification(self, data: dict) -> Response:
        errors = None
        try:
            configuration = self._get_configuration(data)
            if not self.configuration or not self.smtp_server or self.configuration != configuration:
                self._connect_to_server(data)
            email = self._build_email(data)
            self.smtp_server.sendmail(data['from'], data['to'], email.as_string())
        except (
                SMTPServerDisconnected, SMTPSenderRefused, socket.error, OSError, IOError, SMTPAuthenticationError
        ) as e:
            errors = [str(e)]
        return self.create_response(data, errors=errors)
