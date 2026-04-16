"""AKShare Historical Dividends Model."""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional
from pydantic import Field, field_validator

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)

import logging
logger = logging.getLogger(__name__)

class AKShareHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """AKShare Historical Dividends Query."""


class AKShareHistoricalDividendsData(HistoricalDividendsData):
    """AKShare Historical Dividends Data. All data is split-adjusted."""
    reported_date: Optional[dateType] = Field(
        default=None,
        description="Earnings Announcement Date.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Record date of the historical dividends.",
    )
    record_date: Optional[dateType] = Field(
        default=None,
        description="Record date of the historical dividends.",
    )
    declaration_date: Optional[dateType] = Field(
        default=None,
        description="Declaration date of the historical dividends.",
    )
    @field_validator(
        "declaration_date",
        "record_date",
        "reported_date",
        "ex_dividend_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Validate dates."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None
    
class AKShareHistoricalDividendsFetcher(
    Fetcher[
        AKShareHistoricalDividendsQueryParams, List[AKShareHistoricalDividendsData]
    ]
):
    """AKShare Historical Dividends Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any],
    ) -> AKShareHistoricalDividendsQueryParams:
        """Transform the query."""
        return AKShareHistoricalDividendsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from AKShare."""
        # pylint: disable=import-outside-toplevel
        from mysharelib.tools import normalize_symbol
        from openbb_akshare.utils.helpers import get_a_dividends, get_hk_dividends

        symbol_b, symbol_f, market = normalize_symbol(query.symbol)
        if market == "HK":
            dividends = get_hk_dividends(symbol_b)
        else:
            dividends = get_a_dividends(symbol_b)

        return dividends

    @staticmethod
    def transform_data(
        query: AKShareHistoricalDividendsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareHistoricalDividendsData]:
        """Transform the data."""
        #return [AKShareHistoricalDividendsData.model_validate(d) for d in data]
        result: List[AKShareHistoricalDividendsData] = []
        for d in data:
            result.append(AKShareHistoricalDividendsData(**d))
        logger.info(
            "Transformed historical dividends completed.\n"
        )        
        return result
