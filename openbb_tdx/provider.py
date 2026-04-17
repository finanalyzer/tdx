from openbb_core.provider.abstract.provider import Provider
from openbb_tdx.models.equity_historical import TdxQuantEquityHistoricalFetcher
from openbb_tdx.models.equity_quote import TdxQuantEquityQuoteFetcher

# mypy: disable-error-code="list-item"

provider = Provider(
    name="tdxquant",
    description="Data provider for TdxQuant.",
    # Only add 'credentials' if they are needed.
    # For multiple login details, list them all here.
    # credentials=["api_key"],
    website="https://tdxquant.com",
    # Here, we list out the fetchers showing what our provider can get.
    # The dictionary key is the fetcher's name, used in the `router.py`.
    fetcher_dict={
        "EquityHistorical": TdxQuantEquityHistoricalFetcher,
        "EquityQuote": TdxQuantEquityQuoteFetcher,
    }
)
