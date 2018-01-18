class NotifierException(Exception):
    """Base notifier exception. Catch this to catch all of :mod:`notifiers` errors"""

    def __init__(self, *args, **kwargs):
        """
        Looks for ``provider``, ``message`` and ``data`` in kwargs
        :param args: Exception arguments
        :param kwargs: Exception kwargs
        """
        self.provider = kwargs['provider']
        self.message = kwargs.pop('message', None)
        self.data = kwargs.pop('data', None)
        self.response = kwargs.pop('response', None)
        super().__init__(self.message)

    def __repr__(self):
        return f'<NotificationError: {self.message}>'


class BadArguments(NotifierException):
    """
    Raised on schema data validation issues

    :param validation_error: The validation error message
    :param args: Exception arguments
    :param kwargs: Exception kwargs
    """

    def __init__(self, validation_error: str, *args, **kwargs):
        kwargs['message'] = f'Error with sent data: {validation_error}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<BadArguments: {self.message}>'


class SchemaError(NotifierException):
    """
    Raised on schema issues, relevant probably when creating or changing a provider schema

    :param schema_error: The schema error that was raised
    :param args: Exception arguments
    :param kwargs: Exception kwargs
    """

    def __init__(self, schema_error: str, *args, **kwargs):
        kwargs['message'] = f'Schema error: {schema_error}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<SchemaError: {self.message}>'


class NotificationError(NotifierException):
    """
    A notification error. Raised after an issue with the sent notification.
    Looks for ``errors`` key word in kwargs.

    :param args: Exception arguments
    :param kwargs: Exception kwargs
    """

    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop('errors', None)
        kwargs['message'] = f'Notification errors: {",".join(self.errors)}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<NotificationError: {self.message}>'


class ResourceError(NotifierException):
    """
    A notifier resource request error, occurs when an error happened in a
     :meth:`notifiers.core.ProviderResource._get_resource` call
    """

    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop('errors', None)
        self.resource = kwargs.pop('resource', None)
        kwargs['message'] = f'Notifier resource errors: {",".join(self.errors)}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<ResourceError: {self.message}>'
