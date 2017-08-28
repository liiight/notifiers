from . import pushover, simplepush

_all_providers = {
    'pushover': pushover.Pushover,
    'simplepush': simplepush.SimplePush
}
