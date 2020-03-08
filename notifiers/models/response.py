from enum import Enum

import requests

from ..exceptions import NotificationError


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class Response:
    """
    A wrapper for the Notification response.

    :param status: Response status string. ``SUCCESS`` or ``FAILED``
    :param provider: Provider name that returned that response. Correlates to :attr:`~notifiers.core.Provider.name`
    :param data: The notification data that was used for the notification
    :param response: The response object that was returned. Usually :class:`requests.Response`
    :param errors: Holds a list of errors if relevant
    """

    def __init__(
        self,
        status: ResponseStatus,
        provider: str,
        data: dict,
        response: requests.Response = None,
        errors: list = None,
    ):
        self.status = status
        self.provider = provider
        self.data = data
        self.response = response
        self.errors = errors

    def __repr__(self):
        return f"<Response,provider={self.provider.capitalize()},status={self.status.value}, errors={self.errors}>"

    def raise_on_errors(self):
        """
        Raises a :class:`~notifiers.exceptions.NotificationError` if response hold errors

        :raises: :class:`~notifiers.exceptions.NotificationError`: If response has errors
        """
        if self.errors:
            raise NotificationError(
                provider=self.provider,
                data=self.data,
                errors=self.errors,
                response=self.response,
            )

    @property
    def ok(self):
        return self.errors is None
