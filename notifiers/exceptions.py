class NotifierException(Exception):
    """Base notifier exception"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class MissingRequired(NotifierException):
    message = 'The following required arguments are missing: {required}'

    def __init__(self, required):
        super(NotifierException).__init__(self.message.format(required=','.join(required)))
        self.required = required
