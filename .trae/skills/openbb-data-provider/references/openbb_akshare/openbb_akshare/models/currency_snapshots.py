"""AKShare Currency Snapshots Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_snapshots import (
    CurrencySnapshotsData,
    CurrencySnapshotsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class AKShareCurrencySnapshotsQueryParams(CurrencySnapshotsQueryParams):
    """AKShare Currency Snapshots Query.

    Source: https://site.financialmodelingprep.com/developer/docs#exchange-prices-quote
    """

    __json_schema_extra__ = {"base": {"multiple_items_allowed": True}}


class AKShareCurrencySnapshotsData(CurrencySnapshotsData):
    """AKShare Currency Snapshots Data."""

    __alias_dict__ = {
        "last_rate": "最新价",
        "open": "今开",
        "high": "最高",
        "low": "最低",
        "base_currency": "代码",
        "counter_currency": "名称",
        "prev_close": "昨收",
        "change": "涨跌额",
        "change_percent": "涨跌幅",
    }

    # symbol: str = Field(
    #     description="Can use CURR1-CURR2 or CURR1CURR2 format."
    # )
    # name: str = Field(
    #     description="Name of currency pair."
    # )
    change: Optional[float] = Field(
        description="The change in the price from the previous close.", default=None
    )
    change_percent: Optional[float] = Field(
        description="The change in the price from the previous close, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent."""
        return v / 100 if v is not None else None


class AKShareCurrencySnapshotsFetcher(
    Fetcher[AKShareCurrencySnapshotsQueryParams, List[AKShareCurrencySnapshotsData]]
):
    """AKShare Currency Snapshots Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareCurrencySnapshotsQueryParams:
        """Transform the query parameters."""
        return AKShareCurrencySnapshotsQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: AKShareCurrencySnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the AKShare endpoint."""
        # pylint: disable=import-outside-toplevel
        import akshare as ak

        forex_spot_em_df = ak.forex_spot_em()
        new_df=forex_spot_em_df.drop(columns=["序号"])

        return new_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareCurrencySnapshotsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareCurrencySnapshotsData]:
        """Filter by the query parameters and validate the model."""
        # pylint: disable=import-outside-toplevel
        return [AKShareCurrencySnapshotsData.model_validate(d) for d in data]
