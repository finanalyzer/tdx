"""AKShare Currency Historical Price Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    amake_request,
    get_querystring,
)
from pydantic import Field


class AKShareCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """AKShare Currency Historical Price Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {"choices": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]},
    }

    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )


class AKShareCurrencyHistoricalData(CurrencyHistoricalData):
    """AKShare Currency Historical Price Data."""

    __alias_dict__ = {
        "date": "日期",
        "open": "今开",
        "high": "最高",
        "low": "最低",
        "close": "最新价",
        "change": "振幅",    
        "symbol": "代码",
        "name": "名称",
        }

    change: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    symbol: str = Field(
        description="Can use CURR1-CURR2 or CURR1CURR2 format."
    )
    name: str = Field(
        description="Name of currency pair."
    )


class AKShareCurrencyHistoricalFetcher(
    Fetcher[
        AKShareCurrencyHistoricalQueryParams,
        List[AKShareCurrencyHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareCurrencyHistoricalQueryParams:
        """Transform the query params. Start and end dates are set to a 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return AKShareCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def extract_data(
        query: AKShareCurrencyHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        import akshare as ak

        forex_hist_em_df = ak.forex_hist_em(symbol=query.symbol)

        return forex_hist_em_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareCurrencyHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareCurrencyHistoricalData]:
        """Return the transformed data."""

        return [AKShareCurrencyHistoricalData.model_validate(d) for d in data]
