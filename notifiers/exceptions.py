class NotifierException(Exception):
    """Base notifier exception"""

    def __init__(self, *args, **kwargs):
        self.provider = kwargs['provider']
        self.message = kwargs.pop('message', None)
        self.data = kwargs.pop('data', None)

    def __str__(self):
        return f'{self.message}'


class BadArguments(NotifierException):
    def __init__(self, validation_error, *args, **kwargs):
        super().__init__(message=f'Error with sent data: {validation_error}', *args, **kwargs)


class SchemaError(NotifierException):
    def __init__(self, schema_error, *args, **kwargs):
        super().__init__(message=f'Schema error: {schema_error}', *args, **kwargs)


class NotificationError(NotifierException):
    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop('errors', None)
        super().__init__(message=f'Notification errors: {",".join(self.errors)}', *args, **kwargs)
