from pydantic import ValidationError


class NotifierException(Exception):
    """Base notifier exception. Catch this to catch all of :mod:`notifiers` errors"""

    def __init__(self, *args, **kwargs):
        """
        Looks for ``provider``, ``message`` and ``data`` in kwargs
        :param args: Exception arguments
        :param kwargs: Exception kwargs
        """
        self.provider = kwargs.get("provider")
        self.message = kwargs.get("message")
        self.data = kwargs.get("data")
        self.response = kwargs.get("response")
        super().__init__(self.message)

    def __repr__(self):
        return f"<NotificationError: {self.message}>"


class SchemaValidationError(NotifierException):
    """
    Raised on schema data validation issues

    :param validation_error: The validation error message
    :param args: Exception arguments
    :param kwargs: Exception kwargs
    """

    def __init__(
        self, validation_error: str, orig_excp: ValidationError, *args, **kwargs
    ):
        kwargs["message"] = f"Error with sent data: {validation_error}"
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<BadArguments: {self.message}>"


class NotificationError(NotifierException):
    """
    A notification error. Raised after an issue with the sent notification.
    Looks for ``errors`` key word in kwargs.

    :param args: Exception arguments
    :param kwargs: Exception kwargs
    """

    def __init__(self, *args, **kwargs):
        # todo improve visibility of original exception
        self.errors = kwargs.pop("errors", None)
        kwargs["message"] = f'Notification errors: {",".join(self.errors)}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<NotificationError: {self.message}>"


class ResourceError(NotifierException):
    """
    A notifier resource request error, occurs when an error happened in a
     :meth:`notifiers.core.ProviderResource._get_resource` call
    """

    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop("errors", None)
        self.resource = kwargs.pop("resource", None)
        kwargs["message"] = f'Notifier resource errors: {",".join(self.errors)}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<ResourceError: {self.message}>"


class NoSuchNotifierError(NotifierException):
    """
    An unknown notifier was requests, one that was not registered
    """

    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        kwargs["message"] = f"No such notifier with name {name}"
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<NoSuchNotifierError: {self.name}>"
