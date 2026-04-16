"""openbb_tdx OpenBB Platform Provider."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tdx.models.example import ExampleFetcher
from openbb_tdx.models.tdx import TdxPriceFetcher

# mypy: disable-error-code="list-item"

provider = Provider(
    name="openbb_tdx",
    description="Data provider for TdxQuant.",
    # Only add 'credentials' if they are needed.
    # For multiple login details, list them all here.
    # credentials=["api_key"],
    website="https://tdxquant.com",
    # Here, we list out the fetchers showing what our provider can get.
    # The dictionary key is the fetcher's name, used in the `router.py`.
    fetcher_dict={
        "Example": ExampleFetcher,
        "TdxPrice": TdxPriceFetcher,
    }
)
