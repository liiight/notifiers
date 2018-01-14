import logging

from ._version import __version__
from .core import get_notifier, all_providers

logger = logging.getLogger('notifiers').addHandler(logging.NullHandler())
