"""TdxQuant helpers module."""

# pylint: disable=unused-argument,too-many-arguments,too-many-branches,too-many-locals,too-many-statements
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from openbb_core.provider.utils.errors import EmptyDataError
from pandas import DataFrame
from datetime import (
    date as dateType,
    datetime,
    timedelta
)
from tqcenter import tq
import logging
from mysharelib.table_cache import TableCache
from mysharelib.blob_cache import BlobCache
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_tdx import project_name

# Setup logger
setup_logger(project_name)
logger = logging.getLogger(__name__)

EQUITY_HISTORY_SCHEMA = {
    "date": "TEXT PRIMARY KEY",
    "open": "REAL",
    "high": "REAL",
    "low": "REAL",
    "close": "REAL",
    "volume": "REAL",
    "vwap": "REAL",
    "change": "REAL",
    "change_percent": "REAL",
    "amount": "REAL"
}


def tdx_download_without_cache(
        symbol: str,
        start_date: str,
        end_date: str,
        period: Optional[str] = "daily",
        use_cache: Optional[bool] = True, 
    ) -> DataFrame:
    """
    Downloads historical equity data without using cache.
    Parameters:
    symbol: str
        Stock symbol to fetch data for.
    start_date (str): Start date for fetching data in 'YYYYMMDD' format.
    end_date (str): End date for fetching data in 'YYYYMMDD' format.
    period: str
        Data frequency, e.g., "daily", "weekly", "monthly".
    use_cache: bool
        Whether to use cache for fetching data.
    """

    if not symbol:
        raise EmptyDataError("Symbol cannot be empty.")

    symbol_b, symbol_f, market = normalize_symbol(symbol)
    
    # Initialize TdxQuant
    tq.initialize(__file__)
    
    try:
        # Map period to TdxQuant format
        period_map = {
            "daily": "1d",
            "weekly": "1w",
            "monthly": "1m"
        }
        tdx_period = period_map.get(period, "1d")
        
        # Format stock code for TdxQuant
        stock_code = f"{symbol_b}.{market}"
        
        # Calculate count based on period
        # This is a rough estimate, adjust as needed
        start_date_obj = datetime.strptime(start_date, "%Y%m%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y%m%d").date()
        days_diff = (end_date_obj - start_date_obj).days
        
        if period == "daily":
            count = days_diff + 1
        elif period == "weekly":
            count = (days_diff // 7) + 1
        elif period == "monthly":
            count = ((end_date_obj.year - start_date_obj.year) * 12) + (end_date_obj.month - start_date_obj.month) + 1
        else:
            count = 365
        
        # Get market data from TdxQuant
        data_dict = tq.get_market_data(
            field_list=[],
            stock_list=[stock_code],
            start_time=start_date,
            end_time=end_date,
            period=tdx_period,
            count=count,
            dividend_type='none',
            fill_data=False
        )
        
        # Check if we have data
        if data_dict and isinstance(data_dict, dict):
            # Create a new DataFrame
            df = pd.DataFrame()
            
            # Extract data from each field
            for field, field_df in data_dict.items():
                if isinstance(field_df, pd.DataFrame) and stock_code in field_df.columns:
                    # Extract the column for our symbol
                    df[field.lower()] = field_df[stock_code]
            
            if not df.empty:
                # Convert index to date column
                df['date'] = df.index
                if hasattr(df['date'].iloc[0], 'strftime'):
                    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                else:
                    df['date'] = df['date'].astype(str)
                
                # Calculate change and change_percent
                if 'close' in df.columns:
                    df['change'] = df['close'].diff()
                    df['change_percent'] = df['change'] / df['close'].shift(1) * 100
                    # Fill NaN values
                    df['change'] = df['change'].fillna(0)
                    df['change_percent'] = df['change_percent'].fillna(0)
                
                # Reorder columns
                columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'change', 'change_percent']
                # Only include columns that exist in the DataFrame
                columns = [col for col in columns if col in df.columns]
                df = df[columns]
                
                return df
    except Exception as e:
        logger.error(f"Error downloading data from TdxQuant: {e}")
    finally:
        tq.close()
    
    return pd.DataFrame()

def check_cache(symbol: str, 
        cache: TableCache,
        api_key : Optional[str] = "",
        period: Optional[str] = "daily"
        ) -> bool:
    """
    Check if the cache contains the latest data for the given symbol.
    """
    from mysharelib.tools import last_closing_day
    from mysharelib.em.orginfo import get_listing_date
    
    start = get_listing_date(symbol)
    end = last_closing_day()
    # Please note that the format of the date string must be "YYYY-MM-DD" in database.
    cache_df = cache.fetch_date_range(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    cache_df = cache_df.set_index('date')
    cache_df.index = pd.to_datetime(cache_df.index)
    is_cache_valid = cache_df.index.max().date() == last_closing_day()
    if not is_cache_valid:
        logger.warning(f"Cache for {symbol} is not up-to-date. Last date in cache: {cache_df.index.max().date()}, expected: {last_closing_day()}.")
        data_util_today_df = tdx_download_without_cache(symbol, period=period, start_date=start.strftime("%Y%m%d"), end_date=end.strftime("%Y%m%d"))
        cache.write_dataframe(data_util_today_df)
    return is_cache_valid


def tdx_download(
        symbol: str,
        start_date: Optional[dateType] = None,
        end_date: Optional[dateType] = None,
        period: Optional[str] = "daily",
        use_cache: Optional[bool] = True,
        api_key: Optional[str] = "",
    ) -> DataFrame:
    from mysharelib.tools import get_valid_date
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).date()
    if end_date is None: 
        end_date = datetime.now().date()
    start_dt = get_valid_date(start_date)
    end_dt = get_valid_date(end_date)

    # Retrieve data from cache first
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    
    if use_cache:
        cache = TableCache(EQUITY_HISTORY_SCHEMA, project=project_name, table_name=f"{market}{symbol_b}", primary_key="date")
        check_cache(symbol=symbol_b, cache=cache, api_key=api_key, period=period)
        data_from_cache = cache.fetch_date_range(start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
        if not data_from_cache.empty:
            logger.info(f"Getting equity {symbol} historical data from cache...")
            return data_from_cache

    # For now, we'll directly download data without caching
    # Cache implementation can be added later if needed
    data_df = tdx_download_without_cache(
        symbol=symbol, 
        period=period, 
        start_date=start_dt.strftime("%Y%m%d"),
        end_date=end_dt.strftime("%Y%m%d")
    )
    
    if use_cache:
        cache.write_dataframe(data_df)

    return data_df


def get_exchange_name_from_symbol(symbol: str) -> str:
    """Get exchange name from stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., '000001.SZ', '600000.SH')
    
    Returns:
        Exchange name in Chinese
    
    Example:
        >>> get_exchange_name_from_symbol('000001.SZ')
        '深圳交易所'
        >>> get_exchange_name_from_symbol('600000.SH')
        '上海交易所'
    """
    from openbb_tdx.utils.constants import get_exchange_name
    
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    return get_exchange_name(market)


VALID_STATEMENT_TYPES = ["balance_sheet", "income_statement", "cash_flow"]



def get_financial_statement_data(
    symbol: str,
    statement_type: str,
    period: str = "annual",
    use_cache: bool = True,
    limit: int = 5,
) -> DataFrame:
    """Get financial statement data for a given symbol.

    Parameters
    ----------
    symbol : str
        Stock symbol (e.g., '600519.SH')
    statement_type : str
        Type of financial statement: 'balance_sheet', 'income_statement', or 'cash_flow'
    period : str
        Reporting period: 'annual' or 'quarter'
    use_cache : bool
        Whether to use cached data if available
    limit : int
        Maximum number of periods to return

    Returns
    -------
    DataFrame
        Financial statement data as a pandas DataFrame
    """
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    
    if statement_type not in VALID_STATEMENT_TYPES:
        raise ValueError(f"Invalid statement_type: {statement_type}. Must be one of {VALID_STATEMENT_TYPES}")

    cache = BlobCache(table_name=statement_type, project=project_name)
    logger.info(f"Fetching {statement_type} data for {symbol} with limit {limit} and use_cache={use_cache}")

    fetch_func = _get_fetch_func(statement_type)
    return cache.load_cached_data(symbol_f, period, use_cache, fetch_func, limit)


def _get_fetch_func(statement_type: str):
    """Get the appropriate fetch function for the statement type."""
    def fetch_balance_sheet(symbol: str, period: str = "annual", limit: int = 5) -> DataFrame:
        return _fetch_financial_statement_data(symbol, statement_type, period, limit)

    def fetch_income_statement(symbol: str, period: str = "annual", limit: int = 5) -> DataFrame:
        return _fetch_financial_statement_data(symbol, statement_type, period, limit)

    def fetch_cash_flow(symbol: str, period: str = "annual", limit: int = 5) -> DataFrame:
        return _fetch_financial_statement_data(symbol, statement_type, period, limit)

    if statement_type == "balance_sheet":
        return fetch_balance_sheet
    elif statement_type == "income_statement":
        return fetch_income_statement
    elif statement_type == "cash_flow":
        return fetch_cash_flow
    else:
        raise ValueError(f"Unknown statement type: {statement_type}")


def _fetch_financial_statement_data(
    symbol: str,
    statement_type: str,
    period: str = "annual",
    limit: int = 5,
) -> DataFrame:
    """Fetch financial statement data from TdxQuant API.

    Parameters
    ----------
    symbol : str
        Stock symbol (e.g., '600519.SH')
    statement_type : str
        Type of financial statement: 'balance_sheet', 'income_statement', or 'cash_flow'
    period : str
        Reporting period: 'annual' or 'quarter'
    limit : int
        Maximum number of periods to return

    Returns
    -------
    DataFrame
        Financial statement data as a pandas DataFrame
    """
    from openbb_tdx.utils.financial_statement_mapping import (
        BalanceSheetMapper,
        IncomeStatementMapper,
        CashFlowStatementMapper,
    )

    symbol_b, symbol_f, market = normalize_symbol(symbol)
    stock_code = f"{symbol_b}.{market}"

    if statement_type == "balance_sheet":
        mapper = BalanceSheetMapper
    elif statement_type == "income_statement":
        mapper = IncomeStatementMapper
    elif statement_type == "cash_flow":
        mapper = CashFlowStatementMapper
    else:
        raise ValueError(f"Unknown statement type: {statement_type}")

    field_list = mapper.get_field_list()

    mmdd_values = [1231] if period == "annual" else [1231, 930, 630, 331]

    tq.initialize(__file__)

    try:
        latest_data = tq.get_financial_data_by_date(
            stock_list=[stock_code],
            field_list=field_list,
            year=0,
            mmdd=0
        )

        if not latest_data or stock_code not in latest_data:
            logger.warning(f"No {statement_type} data found for {symbol}")
            return pd.DataFrame()

        latest_mapped = mapper.map_from_get_financial_data_by_date(
            latest_data, year=0, mmdd=0
        )
        if stock_code not in latest_mapped:
            logger.warning(f"No {statement_type} data found for {symbol}")
            return pd.DataFrame()

        latest_record = latest_mapped[stock_code]
        period_ending = latest_record.get("period_ending")
        if period_ending:
            if hasattr(period_ending, 'year'):
                current_year = period_ending.year
            else:
                current_year = int(str(period_ending)[:4])
        else:
            from datetime import datetime
            current_year = datetime.now().year

        all_data = []

        if period == "annual":
            for year_offset in range(limit):
                target_year = current_year - year_offset
                tdx_data = tq.get_financial_data_by_date(
                    stock_list=[stock_code],
                    field_list=field_list,
                    year=target_year,
                    mmdd=1231
                )

                if tdx_data and stock_code in tdx_data:
                    mapped_data = mapper.map_from_get_financial_data_by_date(
                        tdx_data, year=target_year, mmdd=1231
                    )
                    if stock_code in mapped_data:
                        record = mapped_data[stock_code]
                        record.pop("query_year", None)
                        record.pop("query_mmdd", None)
                        all_data.append(record)
        else:
            for year_offset in range((limit // 4) + 1):
                target_year = current_year - year_offset
                for mmdd in mmdd_values:
                    if len(all_data) >= limit:
                        break
                    tdx_data = tq.get_financial_data_by_date(
                        stock_list=[stock_code],
                        field_list=field_list,
                        year=target_year,
                        mmdd=mmdd
                    )

                    if tdx_data and stock_code in tdx_data:
                        mapped_data = mapper.map_from_get_financial_data_by_date(
                            tdx_data, year=target_year, mmdd=mmdd
                        )
                        if stock_code in mapped_data:
                            record = mapped_data[stock_code]
                            record.pop("query_year", None)
                            record.pop("query_mmdd", None)
                            all_data.append(record)
                if len(all_data) >= limit:
                    break

        if not all_data:
            logger.warning(f"No {statement_type} data found for {symbol}")
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        return df.head(limit)

    except Exception as e:
        logger.error(f"Error fetching {statement_type} data for {symbol}: {e}")
        return pd.DataFrame()
    finally:
        tq.close()
