"""AKShare Equity Screener Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_screener import (
    EquityScreenerData,
    EquityScreenerQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_akshare.utils.references import EXCHANGES, SECTORS, MARKETS
from pydantic import Field


class AKShareEquityScreenerQueryParams(EquityScreenerQueryParams):
    """AKShare Equity Screener Query."""

    __json_schema_extra__ = {
        "exchange": {
            "multiple_items_allowed": False,
            "choices": EXCHANGES,
        },
        "sector": {
            "multiple_items_allowed": False,
            "choices": SECTORS,
        },
    }

    sector: Optional[str] = Field(default=None, description="Filter by sector.")
    exchange: Optional[str] = Field(
        default=None, description="Filter by exchange."
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )
    limit: Optional[int] = Field(
        default=1000, description="Limit the number of results to return."
    )


class AKShareEquityScreenerData(EquityScreenerData):
    """AKShare Equity Screener Data."""

    __alias_dict__ = {
        "symbol": "代码",
        "name": "名称",
    }

    sector: Optional[str] = Field(
        description="The sector the ticker belongs to.", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange code the asset trades on.",
        default=None,
    )


class AKShareEquityScreenerFetcher(
    Fetcher[
        AKShareEquityScreenerQueryParams,
        List[AKShareEquityScreenerData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquityScreenerQueryParams:
        """Transform the query."""
        return AKShareEquityScreenerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareEquityScreenerQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_akshare.utils.fetch_quote import load_cached_data
        all_df = pd.DataFrame()
        def get_all():
            df1 = pd.DataFrame()
            for exchange in EXCHANGES:
                if exchange not in MARKETS:
                    raise ValueError(f"Exchange {exchange} not supported")
                market = MARKETS[exchange]
                df2 = load_cached_data(market, query.use_cache)
                df1 = pd.concat([df1, df2])
            return df1
            
        if query.exchange not in MARKETS:
            all_df = get_all()
        else:
            market = MARKETS[query.exchange]
            all_df = load_cached_data(market, query.use_cache)

        if query.limit  is not None:
            all_df = all_df[: query.limit]

        return all_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareEquityScreenerQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareEquityScreenerData]:
        """Return the transformed data."""
        return [AKShareEquityScreenerData.model_validate(d) for d in data]
