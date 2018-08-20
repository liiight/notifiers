import copy
import logging
import sys

import notifiers
from notifiers.exceptions import NotifierException


class NotificationHandler(logging.Handler):
    """A :class:`logging.Handler` that enables directly sending log messages to notifiers"""

    def __init__(self, provider: str, defaults: dict = None, **kwargs):
        """
        Sets ups the handler

        :param provider: Provider name to use
        :param defaults: Default provider data to use. Can fallback to environs
        :param kwargs: Additional kwargs
        """
        self.defaults = defaults or {}
        self.provider = None
        self.fallback = None
        self.fallback_defaults = None
        self.init_providers(provider, kwargs)
        super().__init__(**kwargs)

    def init_providers(self, provider, kwargs):
        """
        Inits main and fallback provider if relevant

        :param provider: Provider name to use
        :param kwargs: Additional kwargs
        :raises ValueError: If provider name or fallback names are not valid providers, a :exc:`ValueError` will
         be raised
        """
        self.provider = notifiers.get_notifier(provider, strict=True)
        if kwargs.get("fallback"):
            self.fallback = notifiers.get_notifier(kwargs.pop("fallback"), strict=True)
            self.fallback_defaults = kwargs.pop("fallback_defaults", {})

    def emit(self, record):
        """
        Override the :meth:`~logging.Handler.emit` method that takes the ``msg`` attribute from the log record passed

        :param record: :class:`logging.LogRecord`
        """
        data = copy.deepcopy(self.defaults)
        data["message"] = self.format(record)
        try:
            self.provider.notify(raise_on_errors=True, **data)
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = self.provider.name
        return "<%s %s(%s)>" % (self.__class__.__name__, name, level)

    def handleError(self, record):
        """
        Handles any errors raised during the :meth:`emit` method. Will only try to pass exceptions to fallback notifier
        (if defined) in case the exception is a sub-class of :exc:`~notifiers.exceptions.NotifierException`

        :param record: :class:`logging.LogRecord`
        """
        if logging.raiseExceptions:
            t, v, tb = sys.exc_info()
            if issubclass(t, NotifierException) and self.fallback:
                msg = f"Could not log msg to provider '{self.provider.name}'!\n{v}"
                self.fallback_defaults["message"] = msg
                self.fallback.notify(**self.fallback_defaults)
            else:
                super().handleError(record)
