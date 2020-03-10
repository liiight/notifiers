import pytest

from notifiers.core import _all_providers


@pytest.mark.parametrize("provider", _all_providers.values())
def test_provider_metadata(provider):
    provider = provider()
    assert provider.metadata == {
        "base_url": provider.base_url,
        "site_url": provider.site_url,
        "name": provider.name,
    }
