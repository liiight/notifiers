import logging

from ._version import __version__
from .core import all_providers, get_notifier, notify

logging.getLogger("notifiers").addHandler(logging.NullHandler())

__all__ = ["__version__", "all_providers", "get_notifier", "notify"]
