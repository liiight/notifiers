class NotificationResponse(object):
    def __init__(self, provider_name, status, errors, response=None):
        self.provider_name = provider_name
        self.status = status
        self.error = errors
        self.response = response
