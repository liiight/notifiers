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


class NotificationError(NotifierException):
    pass


class MissingRequired(NotifierException):
    message = 'The following required arguments are missing: {required}'

    def __init__(self, required):
        super(NotifierException).__init__(self.message.format(required=','.join(required)))
        self.required = required
