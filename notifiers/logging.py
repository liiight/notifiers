import copy
import logging
import sys

import notifiers
from notifiers.exceptions import NotifierException


class NotificationHandler(logging.Handler):

    def __init__(self, provider, defaults=None, **kwargs):
        self.defaults = defaults or {}
        self.provider = None
        self.fallback = None
        self.fallback_defaults = None
        self.init_providers(provider, kwargs)
        super().__init__(**kwargs)

    def init_providers(self, provider, kwargs):
        self.provider = notifiers.get_notifier(provider, strict=True)
        if kwargs.get('fallback'):
            self.fallback = notifiers.get_notifier(kwargs.pop('fallback'), strict=True)
            self.fallback_defaults = kwargs.pop('fallback_defaults', None)

    def emit(self, record):
        data = copy.deepcopy(self.defaults)
        data['message'] = self.format(record)
        try:
            self.provider.notify(raise_on_errors=True, **data)
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = self.provider.name
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)

    def handleError(self, record):
        if logging.raiseExceptions:
            t, v, tb = sys.exc_info()
            if issubclass(t, NotifierException) and self.fallback:
                msg = f"Could not log msg to provider '{self.provider.name}'!\n{v}"
                self.fallback_defaults['message'] = msg
                self.fallback.notify(**self.fallback_defaults)
            else:
                super().handleError(record)
