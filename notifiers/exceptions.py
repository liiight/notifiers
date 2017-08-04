class NotifierException(Exception):
    """Base notifier exception"""

    def __init__(self, *args, **kwargs):
        self.provider = kwargs['provider']
        self.message = kwargs.pop('message', None)
        self.data = kwargs.pop('data', None)

    def __repr__(self):
        return f'<NotificationError: {self.message}>'

    __str__ = __repr__


class BadArguments(NotifierException):
    def __init__(self, validation_error, *args, **kwargs):
        kwargs['message'] = f'Error with sent data: {validation_error}'
        super().__init__(*args, **kwargs)


class SchemaError(NotifierException):
    def __init__(self, schema_error, *args, **kwargs):
        kwargs['message'] = f'Schema error: {schema_error}'
        super().__init__(*args, **kwargs)


class NotificationError(NotifierException):
    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop('errors', None)
        kwargs['message'] = f'Notification errors: {",".join(self.errors)}'
        super().__init__(*args, **kwargs)
