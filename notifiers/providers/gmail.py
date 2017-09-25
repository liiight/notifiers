from . import email


class Gmail(email.SMTP):
    site_url = 'https://www.google.com/gmail/about/'
    base_url = 'smtp.gmail.com'
    provider_name = 'gmail'

    @property
    def defaults(self) -> dict:
        data = super().defaults
        data['host'] = self.base_url
        data['port'] = 587
        data['tls'] = True
        return data
