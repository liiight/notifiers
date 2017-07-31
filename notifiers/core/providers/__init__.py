from . import pushover

all_providers = {
    'pushover': pushover.Pushover
}

__all__ = ['all_providers']
