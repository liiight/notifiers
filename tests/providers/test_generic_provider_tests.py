import pytest

from notifiers.core import _all_providers
from notifiers.exceptions import BadArguments


@pytest.mark.parametrize("provider", _all_providers.values())
class TestProviders:
    def test_provider_metadata(self, provider):
        provider = provider()
        assert provider.metadata == {
            "base_url": provider.base_url,
            "site_url": provider.site_url,
            "name": provider.name,
        }

    def test_missing_required(self, provider, subtests):
        provider = provider()
        data = {}
        for arg in provider.required:
            with subtests.test(msg=f"testing arg {arg}", arg=arg):
                with pytest.raises(BadArguments):
                    provider.notify(**data)
                data[arg] = "foo"
