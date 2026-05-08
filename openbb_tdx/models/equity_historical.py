"""TdxQuant Equity Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class TdxQuantEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """TdxQuant Equity Historical Price Query.

    Source: https://tdxquant.com/api
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "period": {"choices": ["daily", "weekly", "monthly"]},
    }

    period: Literal["daily", "weekly", "monthly"] = Field(
        default="daily", description=QUERY_DESCRIPTIONS.get("period", "")
    )

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )

    adjustment: Optional[Literal["qfq", "hfq"]] = Field(
        default=None,
        description="Adjustment type for historical prices. 'qfq' for forward-adjusted (前复权), 'hfq' for backward-adjusted (后复权). None means no adjustment.",
    )


class TdxQuantEquityHistoricalData(EquityHistoricalData):
    """TdxQuant Equity Historical Price Data."""

    __alias_dict__ = {
        "date": "日期",
        "open": "开盘",
        "close": "收盘",
        "high": "最高",
        "low": "最低",
        "volume": "成交量",
        "change": "涨跌额",
        "change_percent": "涨跌幅",
    }

    amount: Optional[float] = Field(
        default=None,
        description="Amount.",
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class TdxQuantEquityHistoricalFetcher(
    Fetcher[
        TdxQuantEquityHistoricalQueryParams,
        List[TdxQuantEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TdxQuantEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: TdxQuantEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""
        from openbb_tdx.utils.helpers import tdx_download
        data = tdx_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            period=query.period,
            use_cache=query.use_cache,
            adjustment=query.adjustment,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TdxQuantEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TdxQuantEquityHistoricalData]:
        """Return the transformed data."""

        return [
            TdxQuantEquityHistoricalData.model_validate(d)
            for d in data
        ]
