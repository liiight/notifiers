from ._version import __version__
from .core import *

logging.getLogger("notifiers").addHandler(logging.NullHandler())

__all__ = ["get_notifier", "all_providers", "notify", "__version__"]
