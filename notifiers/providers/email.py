import socket
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTPAuthenticationError, SMTPServerDisconnected, SMTPSenderRefused

from ..core import Provider, Response
from ..utils.json_schema import one_or_more, list_to_commas
from ..exceptions import NotificationError

DEFAULT_SUBJECT = 'New email from \'notifiers\'!'
DEFAULT_FROM = 'email@notifiers.py'
DEFAULT_SMTP_HOST = 'localhost'


class SMTP(Provider):
    base_url = None
    site_url = 'https://en.wikipedia.org/wiki/Email'
    provider_name = 'email'

    def __init__(self):
        self.smtp_server = None
        self.configuration = None

    @property
    def schema(self) -> dict:
        return {
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
            'required': ['message', 'to'],
            'dependencies': {
                'username': ['password'],
                'password': ['username'],
                'ssl': ['tls']
            },
            'additionalProperties': False,
        }

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
        data = self._merge_defaults(data)
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
        try:
            self.mail_server = smtplib.SMTP_SSL if data['ssl'] else smtplib.SMTP
            self.mail_server = self.mail_server(data['host'], data['port'])
            if data['tls']:
                self.mail_server.ehlo()
                self.mail_server.starttls()
                self.mail_server.ehlo()
        except (socket.error, OSError) as e:
            raise NotificationError(provider=self.provider_name, errors=[str(e)], data=data)

        try:
            if data.get('username'):
                self.mail_server.login(data['username'], data['password'])
        except (IOError, SMTPAuthenticationError) as e:
            raise NotificationError(provider=self.provider_name, errors=[str(e)], data=data)

    def notify(self, **kwargs: dict) -> Response:
        configuration = {kwargs['host'], kwargs['port'], kwargs.get('username')}

