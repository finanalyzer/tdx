"""TdxQuant Equity Search Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field
from mysharelib.tools import normalize_symbol
import logging
from openbb_tdx import project_name
from openbb_tdx.utils.constants import MARKET_CATEGORY_MAP
from openbb_tdx.utils.tdx_equity_search import get_symbols

logger = logging.getLogger(__name__)


class TdxQuantEquitySearchQueryParams(EquitySearchQueryParams):
    """TdxQuant Equity Search Query.
    """

    query: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("query", ""),
    )
    market: str = Field(
        default=MARKET_CATEGORY_MAP["ALL_A_SHARES"],
        description="Market type. Default: '5' (all A-shares)",
    )
    list_type: int = Field(
        default=1,
        description="Return format. 0: only codes, 1: codes and names",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request.",
    )
    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class TdxQuantEquitySearchData(EquitySearchData):
    """TdxQuant Equity Search Data."""


class TdxQuantEquitySearchFetcher(
    Fetcher[
        TdxQuantEquitySearchQueryParams,
        List[TdxQuantEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def _is_valid_symbol(query_str: str) -> bool:
        """Check if the query string is a valid symbol format.
        
        Valid formats:
        - 5 or 6 digit numeric string (e.g., "000001", "00300")
        - Symbol with market suffix (e.g., "600000.SH", "00700.HK")
        """
        if not query_str:
            return False
        
        suffixes = [".SS", ".SH", ".HK", ".BJ", ".SZ"]
        for suffix in suffixes:
            if query_str.endswith(suffix):
                base = query_str[:-len(suffix)]
                return base.isdigit() and len(base) in [5, 6]
        
        return query_str.isdigit() and len(query_str) in [5, 6]

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantEquitySearchQueryParams:
        """Transform the query."""
        query = params.get("query")
        explicit_market = params.get("market")
        if query and TdxQuantEquitySearchFetcher._is_valid_symbol(query) and not explicit_market:
            try:
                _, _, market = normalize_symbol(query)
                if market in ["SH", "SZ", "BJ"]:
                    params["market"] = MARKET_CATEGORY_MAP["ALL_A_SHARES"]
                elif market == "HK":
                    params["market"] = MARKET_CATEGORY_MAP["HONG_KONG_STOCKS"]
            except Exception as e:
                logger.warning(f"Failed to normalize symbol '{query}': {e}")
        
        return TdxQuantEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TdxQuantEquitySearchQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""

        list_type = 0
        if query.market != "102":
            list_type = query.list_type
        
        df = get_symbols(
            use_cache=query.use_cache,
            market=query.market,
            list_type=list_type,
        )
        
        if query.limit is not None and query.limit > 0:
            df = df.head(query.limit)
        
        result = []
        for _, row in df.iterrows():
            result.append({
                "Code": row.get("symbol", ""),
                "Name": row.get("name", ""),
                "Exchange": row.get("exchange", ""),
            })
        
        return result

    @staticmethod
    def transform_data(
        query: TdxQuantEquitySearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TdxQuantEquitySearchData]:
        """Transform the data to the standard format."""

        transformed_data = []
        
        for item in data:
            symbol = item.get('Code', '')
            name = item.get('Name', '')
            exchange = item.get('Exchange', '')
            
            equity_data = TdxQuantEquitySearchData(
                symbol=symbol,
                name=name,
                exchange=exchange
            )
            transformed_data.append(equity_data)
        
        # Filter results if query is provided
        if query.query:
            # Remove exchange suffixes if the query is a symbol
            search_query = query.query
            suffixes = [".SS", ".SH", ".HK", ".BJ", ".SZ"]
            for suffix in suffixes:
                if search_query.endswith(suffix):
                    search_query = search_query[:-len(suffix)]
                    break
            
            filtered = [
                d for d in transformed_data
                if search_query.lower() in d.symbol.lower() or search_query.lower() in d.name.lower()
            ]
            logger.info(f"Searching for {search_query} and found {len(filtered)} results.")
            return filtered

        return transformed_data