import pytest

from notifiers.models.resource import provider_registry


@pytest.mark.parametrize("provider", provider_registry.values())
class TestProviders:
    def test_provider_metadata(self, provider):
        provider = provider()
        assert provider.metadata == {
            "base_url": provider.base_url,
            "site_url": provider.site_url,
            "name": provider.name,
        }
