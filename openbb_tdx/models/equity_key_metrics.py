"""TdxQuant Equity Key Metrics Model.

This module implements the TdxQuant Equity Key Metrics data provider for the OpenBB Platform.
It provides functionality to fetch equity fundamental key metrics from TdxQuant API.

Classes:
    TdxQuantKeyMetricsQueryParams: Query parameters for TdxQuant Key Metrics
    TdxQuantKeyMetricsData: Data model for TdxQuant Key Metrics
    TdxQuantKeyMetricsFetcher: Fetcher for TdxQuant Key Metrics data
"""

# pylint: disable=unused-argument

from datetime import date as dateType, datetime
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
from pydantic import Field, field_validator

import logging
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_tdx import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)


class TdxQuantKeyMetricsQueryParams(KeyMetricsQueryParams):
    """TdxQuant Key Metrics Query Parameters.

    Attributes:
        symbol (str): Symbol representing the entity requested in the data.
            Multiple items allowed, separated by commas.
        period (Literal[annual, quarter]): Reporting period.
            Defaults to quarter.
        use_cache (bool): Whether to use a cached request.
            The quote is cached for one hour.
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "period": {"choices": ["annual", "quarter"]},
    }

    period: Literal["annual", "quarter"] = Field(
        default="quarter",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class TdxQuantKeyMetricsData(KeyMetricsData):
    """TdxQuant Key Metrics Data.

    This model represents equity key metrics data retrieved from TdxQuant
    and transformed to OpenBB's standard format.

    Attributes:
        symbol (str): Symbol representing the entity requested in the data.
        period_ending (date): End date of the reporting period.
        fiscal_year (int): Fiscal year for the fiscal period.
        fiscal_period (str): Fiscal period for the data (Q1, Q2, Q3, Q4).
        currency (str): Currency in which the data is reported.
        market_cap (float): Market capitalization.
        pe_ratio (float): Price-to-earnings ratio (TTM).
        forward_pe (float): Forward price-to-earnings ratio.
        eps (float): Earnings per share.
        price_to_book (float): Price-to-book ratio.
        book_value_per_share (float): Book value per share.
        debt_to_equity (float): Debt-to-equity ratio.
        current_ratio (float): Current ratio.
        quick_ratio (float): Quick ratio.
        gross_margin (float): Gross margin.
        profit_margin (float): Profit margin.
        operating_margin (float): Operating margin.
        return_on_assets (float): Return on assets.
        return_on_equity (float): Return on equity.
        dividend_yield (float): Dividend yield.
        enterprise_value (float): Enterprise value.
        ev_to_sales (float): Enterprise value to sales ratio.
        beta (float): Beta coefficient.
        year_high (float): 52-week high.
        year_low (float): 52-week low.
        working_capital (float): Working capital.
        total_debt (float): Total debt.
        operating_cash_flow (float): Operating cash flow.
        ebit_margin (float): EBIT margin.
        price_to_sales (float): Price-to-sales ratio.
        price_to_cash (float): Price-to-cash ratio.
        cash_per_share (float): Cash per share.
    """

    __alias_dict__ = {
        "symbol": "symbol",
        "fiscal_period": "fiscal_period",
        "period_ending": "period_ending",
        "market_cap": "market_cap",
        "pe_ratio": "pe_ratio",
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def validate_period_ending(cls, v):
        """Validate and transform period_ending date.

        Parameters
        ----------
        v : str, date, datetime, or None
            Input value to validate

        Returns
        -------
        date or None
            Parsed date object or None if invalid
        """
        import math
        if v is None or v == "":
            return None
        if isinstance(v, dateType):
            return v
        if isinstance(v, datetime):
            return v.replace(hour=0, minute=0, second=0, microsecond=0).date()
        try:
            if isinstance(v, str) and len(v) == 10:
                return datetime.strptime(v, "%Y-%m-%d").date()
            elif isinstance(v, str) and len(v) == 8:
                return datetime.strptime(v, "%Y%m%d").date()
            f = float(v)
            if math.isnan(f) or math.isinf(f):
                return None
        except (ValueError, TypeError):
            pass
        return None

    @field_validator(
        "market_cap", "pe_ratio", "forward_pe", "eps", "price_to_book",
        "book_value_per_share", "debt_to_equity", "current_ratio",
        "quick_ratio", "gross_margin", "profit_margin", "operating_margin",
        "return_on_assets", "return_on_equity", "dividend_yield",
        "enterprise_value", "ev_to_sales", "beta", "year_high", "year_low",
        "working_capital", "total_debt", "operating_cash_flow",
        "ebit_margin", "price_to_sales", "price_to_cash", "cash_per_share",
        mode="before", check_fields=False
    )
    @classmethod
    def validate_numeric_fields(cls, v):
        """Validate numeric financial fields.

        Parameters
        ----------
        v : str, float, int, or None
            Input value to validate

        Returns
        -------
        float or None
            Validated numeric value or None if invalid
        """
        import math
        if v is None or v == "":
            return None
        try:
            f = float(v)
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        except (ValueError, TypeError):
            return None

    @field_validator("fiscal_year", mode="before", check_fields=False)
    @classmethod
    def validate_fiscal_year(cls, v):
        """Validate fiscal year field.

        Parameters
        ----------
        v : str, int, float, or None
            Input value to validate

        Returns
        -------
        int or None
            Validated year or None if invalid
        """
        import math
        if v is None or v == "":
            return None
        try:
            f = float(v)
            if math.isnan(f) or math.isinf(f):
                return None
            return int(f)
        except (ValueError, TypeError):
            return None


class TdxQuantKeyMetricsFetcher(
    Fetcher[
        TdxQuantKeyMetricsQueryParams,
        List[TdxQuantKeyMetricsData],
    ]
):
    """TdxQuant Key Metrics Fetcher.

    This class is responsible for fetching equity key metrics data from TdxQuant API.
    It implements the three required methods for a Fetcher:
    - transform_query: Transforms the query parameters
    - aextract_data: Extracts the raw data from TdxQuant API
    - transform_data: Transforms the raw data into the standard model
    """

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantKeyMetricsQueryParams:
        """Transform the query parameters.

        Args:
            params (Dict[str, Any]): The raw query parameters

        Returns:
            TdxQuantKeyMetricsQueryParams: The transformed query parameters
        """
        return TdxQuantKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TdxQuantKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from TdxQuant API.

        Args:
            query (TdxQuantKeyMetricsQueryParams): The query parameters
            credentials (Optional[Dict[str, str]]): The credentials for TdxQuant API
            **kwargs (Any): Additional keyword arguments

        Returns:
            List[Dict]: The raw data from TdxQuant API
        """
        import asyncio
        from openbb_core.app.model.abstract.error import OpenBBError
        from tqcenter import tq

        try:
            tq.initialize(__file__)
        except Exception as e:
            raise OpenBBError(
                f"Failed to initialize TdxQuant connection. "
                f"Ensure TongDaXin client is running and logged in. Error: {str(e)}"
            )

        symbols = query.symbol.split(",")
        results: List[Dict] = []
        messages: List[str] = []

        async def get_one(symbol: str) -> None:
            """Get key metrics data for one symbol.

            Args:
                symbol (str): The ticker symbol
            """
            try:
                from openbb_tdx.utils.tdx_key_metrics import map_tdx_to_openbb

                symbol_b, symbol_f, market = normalize_symbol(symbol.strip())

                mapped_data = map_tdx_to_openbb(symbol_f, auto_connect=False)

                if mapped_data:
                    mapped_data["symbol"] = symbol.strip()
                    results.append(mapped_data)
                else:
                    messages.append(f"No data returned for symbol {symbol}")

            except Exception as e:
                messages.append(
                    f"Error fetching data for {symbol}: {e.__class__.__name__}: {str(e)}"
                )

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        tq.close()

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if not results and not messages:
            raise EmptyDataError("No data was returned for any symbol")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: TdxQuantKeyMetricsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantKeyMetricsData]:
        """Transform the raw data into the standard model.

        Args:
            query (TdxQuantKeyMetricsQueryParams): The query parameters
            data (List[Dict]): The raw data from TdxQuant API
            **kwargs (Any): Additional keyword arguments

        Returns:
            List[TdxQuantKeyMetricsData]: The transformed data
        """
        return [TdxQuantKeyMetricsData.model_validate(d) for d in data]
