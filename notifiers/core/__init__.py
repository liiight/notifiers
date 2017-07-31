from .providers import all_providers
from .provider import Provider


def get_notifier(provider_name: str) -> Provider:
    return all_providers.get(provider_name.lower())()
