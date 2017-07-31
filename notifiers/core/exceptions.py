class NotifierException(Exception):
    """Base notifier exception"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class BadArguments(NotifierException):
    message = 'Error with sent data: {validation_error}'

    def __init__(self, validation_error):
        super().__init__(self.message.format(validation_error=validation_error))


class SchemaError(NotifierException):
    message = 'Schema error: {schema_error}'

    def __index__(self, schema_error):
        super().__init__(self.message.format(schema_error=schema_error))


class NotificationError(NotifierException):
    pass
