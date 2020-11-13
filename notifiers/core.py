import logging
from typing import List

from .exceptions import NoSuchNotifierError
from .models.resource import provider_registry
from .models.resource import T_Provider
from .models.response import Response

log = logging.getLogger("notifiers")


def get_notifier(provider_name: str, strict: bool = False) -> T_Provider:
    """
    Convenience method to return an instantiated :class:`~notifiers.core.Provider` object according to it ``name``

    :param provider_name: The ``name`` of the requested :class:`~notifiers.core.Provider`
    :param strict: Raises a :class:`ValueError` if the given provider string was not found
    :return: :class:`Provider` or None
    :raises ValueError: In case ``strict`` is True and provider not found
    """
    if provider_name in provider_registry:
        log.debug("found a match for '%s', returning", provider_name)
        return provider_registry[provider_name]()
    elif strict:
        raise NoSuchNotifierError(name=provider_name)


def all_providers() -> List[str]:
    """Returns a list of all :class:`~notifiers.core.Provider` names"""
    return list(provider_registry.keys())


def notify(provider_name: str, **kwargs) -> Response:
    """
    Quickly sends a notification without needing to get a notifier via the :func:`get_notifier` method.

    :param provider_name: Name of the notifier to use. Note that if this notifier name does not exist it will raise a
    :param kwargs: Notification data, dependant on provider
    :return: :class:`Response`
    :raises: :class:`~notifiers.exceptions.NoSuchNotifierError` If ``provider_name`` is unknown,
     will raise notification error
    """
    return get_notifier(provider_name=provider_name, strict=True).notify(**kwargs)
