"""AKShare Equity Ownership Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_ownership import (
    EquityOwnershipData,
    EquityOwnershipQueryParams,
)
from mysharelib.tools import most_recent_quarter
from pydantic import field_validator


class AKShareEquityOwnershipQueryParams(EquityOwnershipQueryParams):
    """AKShare Equity Ownership Query.

    Source: https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index?type=web&code=SH688686#sdgd-0
    """

    @field_validator("date", mode="before", check_fields=True)
    @classmethod
    def time_validate(cls, v: str):
        """Validate the date."""
        if v is None:
            v = dateType.today()
        if isinstance(v, str):
            base = datetime.strptime(v, "%Y-%m-%d").date()
            return most_recent_quarter(base)
        return most_recent_quarter(v)


class AKShareEquityOwnershipData(EquityOwnershipData):
    """AKShare Equity Ownership Data."""


class AKShareEquityOwnershipFetcher(
    Fetcher[
        AKShareEquityOwnershipQueryParams,
        List[AKShareEquityOwnershipData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquityOwnershipQueryParams:
        """Transform the query params."""
        return AKShareEquityOwnershipQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareEquityOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        from openbb_akshare.utils.ak_equity_ownership import stock_gdfx_top_10

        return stock_gdfx_top_10(query.symbol, query.date).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareEquityOwnershipQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareEquityOwnershipData]:
        """Return the transformed data."""
        own = [AKShareEquityOwnershipData.model_validate(d) for d in data]
        own.sort(key=lambda x: x.filing_date, reverse=True)
        return own
