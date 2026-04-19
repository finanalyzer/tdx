"""TdxQuant Equity Search Utility Functions.

This module provides reusable functions for fetching stock symbols from TdxQuant.
"""

import logging
import pandas as pd
from typing import Optional
from mysharelib.tools import setup_logger, get_exchange, normalize_symbol
from mysharelib.table_cache import TableCache
from openbb_tdx import project_name
from openbb_tdx.utils.constants import MARKET_CATEGORY_MAP

try:
    from tqcenter import tq
except ImportError:
    tq = None

setup_logger(project_name)
logger = logging.getLogger(__name__)

SYMBOLS_TABLE_SCHEMA = {
    "symbol": "TEXT PRIMARY KEY",
    "name": "TEXT",
    "exchange": "TEXT",
}


def get_symbols_df(market: str = "5", list_type: int = 1) -> pd.DataFrame:
    """Fetch stock symbols from TdxQuant.

    Args:
        market: Market type code. Default is "5" (all A-shares).
            Common values:
            - "5": All A-shares
            - "102": Hong Kong stocks
            See MARKET_CATEGORY_MAP for all options.
        list_type: Return format. Default is 1.
            - 0: Only codes
            - 1: Codes and names

    Returns:
        pd.DataFrame: DataFrame with columns ['symbol', 'name', 'exchange'].

    Raises:
        ImportError: If tqcenter module is not available.
        RuntimeError: If TdxQuant initialization fails.
    """
    if tq is None:
        logger.error("tqcenter module not found. Please install it first.")
        raise ImportError("tqcenter module not found")

    try:
        tq.initialize(__file__)
    except Exception as e:
        logger.error(f"Failed to initialize TdxQuant: {e}")
        raise RuntimeError(f"Failed to initialize TdxQuant: {e}") from e

    actual_list_type = 0 if market == "102" else list_type

    logger.info(f"Fetching symbols from TdxQuant: market={market}, list_type={actual_list_type}")
    data = tq.get_stock_list(market=market, list_type=actual_list_type)

    result = []
    if actual_list_type == 0:
        for code in data:
            result.append({"symbol": code, "name": ""})
    else:
        for item in data:
            code = item.get("Code", "")
            name = item.get("Name", "")
            result.append({"symbol": code, "name": name})

    df = pd.DataFrame(result)

    def get_exchange_from_symbol(symbol: str) -> str:
        base_code = symbol.split('.')[0] if '.' in symbol else symbol
        try:
            return get_exchange(base_code)
        except ValueError:
            logger.warning(f"Unknown exchange for code: {base_code}")
            return ""

    df["exchange"] = df["symbol"].apply(get_exchange_from_symbol)

    logger.info(f"Fetched {len(df)} symbols from TdxQuant")
    return df


def get_symbols(
    use_cache: bool = True,
    market: str = "5",
    list_type: int = 1,
    cache_table_name: Optional[str] = None,
) -> pd.DataFrame:
    """Get stock symbols with caching support.

    This function retrieves stock symbols from cache if available and not expired,
    otherwise fetches from TdxQuant and caches the result.

    Args:
        use_cache: Whether to use cached data. Default is True.
        market: Market type code. Default is "5" (all A-shares).
            Common values:
            - "5": All A-shares
            - "102": Hong Kong stocks
            See MARKET_CATEGORY_MAP for all options.
        list_type: Return format. Default is 1.
            - 0: Only codes
            - 1: Codes and names
        cache_table_name: Custom cache table name. If None, uses "symbols".

    Returns:
        pd.DataFrame: DataFrame with columns ['symbol', 'name', 'exchange'].

    Example:
        >>> df = get_symbols(use_cache=True, market="5")
        >>> print(df.head())
           symbol    name exchange
        0  000001.SZ  平安银行       SZ
        1  000002.SZ  万科A       SZ
    """
    table_name = cache_table_name or "symbols"
    cache = TableCache(
        SYMBOLS_TABLE_SCHEMA,
        project=project_name,
        table_name=table_name,
        primary_key="symbol",
    )

    if use_cache:
        data = cache.read_dataframe()
        if not data.empty:
            logger.info(f"Loading symbols from {project_name} cache...")
            return data

    logger.info(f"Fetching symbols for {project_name} (market={market}, list_type={list_type})...")
    data = get_symbols_df(market=market, list_type=list_type)
    # Cache the result for future use
    # cache.write_dataframe(data)
    return data


_SYMBOLS_CACHE: Optional[pd.DataFrame] = None


def get_name(symbol: str) -> str:
    """Get the name of a stock symbol.

    This function retrieves the stock name from cached symbols data.
    It searches both A-shares and Hong Kong markets.

    Args:
        symbol: Stock symbol in any format (e.g., "000001.SZ", "000001", "600000.SH").

    Returns:
        str: The stock name, or empty string if not found.

    Example:
        >>> name = get_name("000001.SZ")
        >>> print(name)
        平安银行
    """
    global _SYMBOLS_CACHE

    if not symbol:
        return ""

    symbol_b, symbol_f, market = normalize_symbol(symbol)

    if _SYMBOLS_CACHE is None or _SYMBOLS_CACHE.empty:
        try:
            if market == "HK":
                df = get_symbols(use_cache=True, market=MARKET_CATEGORY_MAP["HONG_KONG_STOCKS"], list_type=0)
            else:
                df = get_symbols(use_cache=True, market=MARKET_CATEGORY_MAP["ALL_A_SHARES"], list_type=1)

            _SYMBOLS_CACHE = df
        except Exception as e:
            logger.warning(f"Failed to load symbols cache: {e}")
            return ""

    if market == "HK":
        filtered_cache = _SYMBOLS_CACHE[_SYMBOLS_CACHE['exchange'] == 'HKEX']
    else:
        filtered_cache = _SYMBOLS_CACHE[_SYMBOLS_CACHE['exchange'] != 'HKEX']

    matches = filtered_cache[filtered_cache['symbol'].str.startswith(symbol_b)]

    if not matches.empty:
        return str(matches.iloc[0]['name'])

    return ""
