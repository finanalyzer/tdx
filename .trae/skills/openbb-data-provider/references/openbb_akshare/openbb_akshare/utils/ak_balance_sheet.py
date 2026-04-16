import pandas as pd
from typing import Any, Literal, Optional
from mysharelib.em.stock_balance_sheet import stock_balance_sheet
from mysharelib.tools import normalize_symbol
import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)

def stock_hk_balance_sheet(symbol: str,
                           limit: int = 10,
                           period: Literal["annual", "quarter"] = "quarter"
                           ) -> pd.DataFrame:
    logger.info(f"Fetching HK balance sheet for {symbol} with limit {limit} and period {period}")
    _, symbol_f, _ = normalize_symbol(symbol)
    df_balance = stock_balance_sheet(symbol_f, limit, period)[['REPORT_DATE','STD_ITEM_NAME','AMOUNT']]

    # Pivot the DataFrame to restructure it
    pivoted_balance = df_balance.pivot(index='STD_ITEM_NAME', columns='REPORT_DATE', values='AMOUNT')

    # Sort the columns in descending order (most recent date first)
    pivoted_balance = pivoted_balance.reindex(sorted(pivoted_balance.columns, reverse=True), axis=1)

    # Reset the index to make STD_ITEM_NAME a regular column
    pivoted_balance = pivoted_balance.T

    # Reset index and rename the index column
    pivoted_balance = pivoted_balance.reset_index()
    pivoted_balance = pivoted_balance.rename(columns={'REPORT_DATE': 'period_ending'})

    return pivoted_balance

def ak_stock_balance_sheet(symbol: str,
                           limit: int = 10,
                           period: Literal["annual", "quarter"] = "quarter"
                           ) -> pd.DataFrame:
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    if market == "HK":
        return stock_hk_balance_sheet(symbol, limit, period)
    else:
        import akshare as ak
        symbol_em = f"{market}{symbol_b}"

        if period == "annual":
            return ak.stock_balance_sheet_by_yearly_em(symbol=symbol_em)
        elif period == "quarter":
            return ak.stock_balance_sheet_by_report_em(symbol=symbol_em)
        else:
            raise ValueError("Invalid period. Please use 'annual' or 'quarter'.")