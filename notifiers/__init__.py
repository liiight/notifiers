import logging

from ._version import __version__
from .core import all_providers
from .core import get_notifier
from .core import notify

logging.getLogger("notifiers").addHandler(logging.NullHandler())

__all__ = ["get_notifier", "all_providers", "notify", "__version__"]
