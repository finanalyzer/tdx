"""AKShare Key Metrics Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class AKShareKeyMetricsQueryParams(KeyMetricsQueryParams):
    """AKShare Key Metrics Query.

    Source: https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=SH600028
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "period": {
            "choices": ["annual", "quarter"],
        },
    }

    period: Literal["annual", "quarter"] = Field(
        default="quarter",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )

class AKShareKeyMetricsData(KeyMetricsData):
    """AKShare Key Metrics Data."""

    __alias_dict__ = {
        "symbol": "证券代码",
        "fiscal_period": "报告类型",
        "period_ending": "报告日期",
        "market_cap": "流通值",
        "pe_ratio": "市盈率(动)",
    }


class AKShareKeyMetricsFetcher(
    Fetcher[
        AKShareKeyMetricsQueryParams,
        List[AKShareKeyMetricsData],
    ]
):
    """AKShare Key Metrics Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareKeyMetricsQueryParams:
        """Transform the query params."""
        return AKShareKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        symbols = query.symbol.split(",")
        results: List = []

        async def get_one(symbol, api_key):
            """Get data for one symbol."""
            from openbb_akshare.utils.ak_key_metrics import fetch_key_metrics
            df_base = fetch_key_metrics(symbol, period=query.period, use_cache=query.use_cache, api_key=api_key)

            results.append(df_base['数值'].to_dict())

        await asyncio.gather(*[get_one(symbol, None) for symbol in symbols])

        if not results:
            raise EmptyDataError(f"No data found for given symbols -> {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: AKShareKeyMetricsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareKeyMetricsData]:
        """Return the transformed data."""
        return [AKShareKeyMetricsData.model_validate(d) for d in data]
