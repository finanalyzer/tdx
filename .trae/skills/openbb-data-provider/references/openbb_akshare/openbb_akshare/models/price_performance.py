"""AKShare Price Performance Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_urls
from pydantic import Field, model_validator


class AKSharePricePerformanceQueryParams(RecentPerformanceQueryParams):
    """AKShare Price Performance Query.

    Source: https://akshare.akfamily.xyz/data/index/index.html#id3
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class AKSharePricePerformanceData(RecentPerformanceData):
    """AKShare Price Performance Data."""

    #symbol: str = Field(description="The ticker symbol.")

    __alias_dict__ = {
        "one_day": "1D",
        "one_week": "5D",
        "one_month": "1M",
        "three_month": "3M",
        "six_month": "6M",
        "one_year": "1Y",
        "three_year": "3Y",
        "five_year": "5Y",
        "ten_year": "10Y",
    }

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Replace zero with None and convert percents to normalized values."""
        if isinstance(values, dict):
            for k, v in values.items():
                if k != "symbol":
                    values[k] = None if v == 0 else float(v) / 100
        return values


class AKSharePricePerformanceFetcher(
    Fetcher[
        AKSharePricePerformanceQueryParams,
        List[AKSharePricePerformanceData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKSharePricePerformanceQueryParams:
        """Transform the query params."""
        return AKSharePricePerformanceQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: AKSharePricePerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        import pandas as pd
        symbols = query.symbol.split(",")

        def get_data(code: str) -> dict:
            from mysharelib.tools import calculate_price_performance, last_closing_day
            from openbb_akshare.utils.helpers import get_list_date, ak_download

            df = ak_download(symbol=code, start_date=get_list_date(code), end_date=last_closing_day())
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return calculate_price_performance(code, df)

        return [get_data(symbol) for symbol in symbols]

    @staticmethod
    def transform_data(
        query: AKSharePricePerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKSharePricePerformanceData]:
        """Return the transformed data."""

        return [AKSharePricePerformanceData.model_validate(i) for i in data]
