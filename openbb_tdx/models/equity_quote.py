"""TdxQuant Equity Quote Model.

This module implements the TdxQuant Equity Quote data provider for the OpenBB Platform.
It provides functionality to fetch real-time and historical stock quotes from TdxQuant API.

Classes:
    TdxQuantEquityQuoteQueryParams: Query parameters for TdxQuant Equity Quote
    TdxQuantEquityQuoteData: Data model for TdxQuant Equity Quote
    TdxQuantEquityQuoteFetcher: Fetcher for TdxQuant Equity Quote data
"""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field
import logging
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_tdx import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)


class TdxQuantEquityQuoteQueryParams(EquityQuoteQueryParams):
    """TdxQuant Equity Quote Query Parameters.

    Attributes:
        symbol (str): Symbol representing the entity requested in the data.
        use_cache (bool): Whether to use a cached request. The quote is cached for one hour.
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class TdxQuantEquityQuoteData(EquityQuoteData):
    """TdxQuant Equity Quote Data Model.

    Attributes:
        symbol (str): Symbol representing the entity requested in the data.
        name (str): Name of the company or asset.
        last_price (float): Price of the last trade.
        open (float): The open price.
        high (float): The high price.
        low (float): The low price.
        prev_close (float): The previous close price.
        volume (int): The trading volume.
        change (float): Change in price from previous close.
        change_percent (float): Change in price as a normalized percentage.
        year_high (float): The one year high (52W High).
        year_low (float): The one year low (52W Low).
        bid (float): Price of the top bid order.
        bid_size (int): Number of round lot orders at the bid price.
        ask (float): Price of the top ask order.
        ask_size (int): Number of round lot orders at the ask price.
        exchange (str): The name or symbol of the venue where the data is from.
        market_center (str): The ID of the UTP participant that originated the message.
        last_size (int): Size of the last trade.
        close (float): The close price.
        exchange_volume (int): Volume of shares exchanged during the trading day on the specific exchange.
    """

    __alias_dict__ = {
        "symbol": "code",
        "name": "name",
        "last_price": "price",
        "open": "open",
        "high": "high",
        "low": "low",
        "prev_close": "prev_close",
        "volume": "volume",
        "change": "change",
        "change_percent": "change_pct",
        "year_high": "year_high",
        "year_low": "year_low",
        "bid": "bid",
        "bid_size": "bid_volume",
        "ask": "ask",
        "ask_size": "ask_volume",
        "exchange": "exchange",
        "market_center": "market_center",
        "last_size": "last_volume",
        "close": "close",
        "volume": "volume",
        "exchange_volume": "exchange_volume",
    }


class TdxQuantEquityQuoteFetcher(
    Fetcher[TdxQuantEquityQuoteQueryParams, List[TdxQuantEquityQuoteData]]
):
    """TdxQuant Equity Quote Fetcher.

    This class is responsible for fetching equity quote data from TdxQuant API.
    It implements the three required methods for a Fetcher:
    - transform_query: Transforms the query parameters
    - extract_data: Extracts the raw data from TdxQuant API
    - transform_data: Transforms the raw data into the standard model
    """

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantEquityQuoteQueryParams:
        """Transform the query parameters.

        Args:
            params (Dict[str, Any]): The raw query parameters

        Returns:
            TdxQuantEquityQuoteQueryParams: The transformed query parameters
        """
        return TdxQuantEquityQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from TdxQuant API.

        Args:
            query (TdxQuantEquityQuoteQueryParams): The query parameters
            credentials (Optional[Dict[str, str]]): The credentials for TdxQuant API
            **kwargs (Any): Additional keyword arguments

        Returns:
            List[Dict]: The raw data from TdxQuant API
        """
        # pylint: disable=import-outside-toplevel
        import os

        symbols = query.symbol.split(",")
        all_data = []

        def get_one(symbol: str, use_cache: bool) -> Dict:
            """Get the data for one ticker symbol.

            Args:
                symbol (str): The ticker symbol
                use_cache (bool): Whether to use cached data

            Returns:
                Dict: The data for the symbol
            """
            try:
                # Import TdxQuant API
                from tqcenter import tq
                
                # Initialize TdxQuant API if not already initialized
                try:
                    # Use current working directory as the initialization path
                    #init_path = os.getcwd()
                    tq.initialize(__file__)
                except Exception as e:
                    logger.warning(f"TdxQuant initialization warning: {e}")

                symbol_b, symbol_f, market = normalize_symbol(symbol)
                
                # Get market snapshot data
                market_snapshot = tq.get_market_snapshot(stock_code=symbol_f, field_list=[])
                
                if not market_snapshot or market_snapshot.get('ErrorId') != '0':
                    error_msg = market_snapshot.get('ErrorId', 'Unknown error') if market_snapshot else 'No data returned'
                    logger.error(f"Error fetching data for symbol {symbol}: {error_msg}")
                    return {"symbol": symbol, "error": str(error_msg)}
                
                # Map TdxQuant API fields to OpenBB standard fields
                # Get exchange name using helper function
                try:
                    from openbb_tdx.utils.helpers import get_exchange_name_from_symbol
                    exchange_name = get_exchange_name_from_symbol(symbol)
                except Exception:
                    exchange_name = symbol.split('.')[-1] if '.' in symbol else "Unknown"
                
                data = {
                    "code": symbol_b,
                    "name": f"Stock {symbol}",  # TdxQuant doesn't provide name in snapshot
                    "price": float(market_snapshot.get('Now', 0)),
                    "open": float(market_snapshot.get('Open', 0)),
                    "high": float(market_snapshot.get('Max', 0)),
                    "low": float(market_snapshot.get('Min', 0)),
                    "prev_close": float(market_snapshot.get('LastClose', 0)),
                    "volume": int(float(market_snapshot.get('Volume', 0))),
                    "change": float(market_snapshot.get('TickDiff', 0)),
                    "change_pct": float(market_snapshot.get('Zangsu', 0)),
                    "year_high": None,  # Not provided by TdxQuant snapshot
                    "year_low": None,  # Not provided by TdxQuant snapshot
                    "bid": float(market_snapshot.get('Buyp', ['0'])[0]) if market_snapshot.get('Buyp') else 0,
                    "bid_volume": int(float(market_snapshot.get('Buyv', ['0'])[0])) if market_snapshot.get('Buyv') else 0,
                    "ask": float(market_snapshot.get('Sellp', ['0'])[0]) if market_snapshot.get('Sellp') else 0,
                    "ask_volume": int(float(market_snapshot.get('Sellv', ['0'])[0])) if market_snapshot.get('Sellv') else 0,
                    "exchange": exchange_name,
                    "market_center": "TdxQuant",
                    "last_volume": int(float(market_snapshot.get('NowVol', 0))),
                    "close": float(market_snapshot.get('Now', 0)),  # Use current price as close for real-time data
                    "exchange_volume": int(float(market_snapshot.get('Volume', 0))),
                }
                
                return data
            except Exception as e:
                logger.error(f"Error fetching data for symbol {symbol}: {e}")
                return {"symbol": symbol, "error": str(e)}

        for symbol in symbols:
            try:
                data = get_one(symbol, use_cache=query.use_cache)
                if "error" not in data:
                    all_data.append(data)
                else:
                    logger.warning(f"Skipping symbol {symbol} due to error: {data.get('error')}")
            except Exception as e:
                logger.error(f"Error processing symbol {symbol}: {e}")
                continue

        return all_data

    @staticmethod
    def transform_data(
        query: TdxQuantEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantEquityQuoteData]:
        """Transform the raw data into the standard model.

        Args:
            query (TdxQuantEquityQuoteQueryParams): The query parameters
            data (List[Dict]): The raw data from TdxQuant API
            **kwargs (Any): Additional keyword arguments

        Returns:
            List[TdxQuantEquityQuoteData]: The transformed data
        """
        return [TdxQuantEquityQuoteData.model_validate(d) for d in data]
