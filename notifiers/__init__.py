import logging

from .core import get_notifier, all_providers

logging.getLogger('notifiers').addHandler(logging.NullHandler())
