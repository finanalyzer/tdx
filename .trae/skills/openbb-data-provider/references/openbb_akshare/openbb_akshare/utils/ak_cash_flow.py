import pandas as pd
from typing import Any, Literal, Optional
from mysharelib.em.stock_cash_flow_sheet import stock_cash_flow_sheet
from mysharelib.tools import normalize_symbol
import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)

def stock_hk_cash_flow(symbol: str,
                      limit: int = 10,
                      period: Literal["annual", "quarter"] = "quarter"
                      ) -> pd.DataFrame:
    logger.info(f"Fetching HK cash flow for {symbol} with limit {limit} and period {period}")
    _, symbol_f, _ = normalize_symbol(symbol)
    df_cash_flow = stock_cash_flow_sheet(symbol_f, limit, period)[['REPORT_DATE', 'STD_ITEM_NAME', 'AMOUNT']]

    # Pivot the DataFrame to restructure it
    pivoted_cash_flow = df_cash_flow.pivot(index='STD_ITEM_NAME', columns='REPORT_DATE', values='AMOUNT')

    # Sort the columns in descending order (most recent date first)
    pivoted_cash_flow = pivoted_cash_flow.reindex(sorted(pivoted_cash_flow.columns, reverse=True), axis=1)

    # Reset the index to make STD_ITEM_NAME a regular column
    pivoted_cash_flow = pivoted_cash_flow.T

    # Reset index and rename the index column
    pivoted_cash_flow = pivoted_cash_flow.reset_index()
    pivoted_cash_flow = pivoted_cash_flow.rename(columns={'REPORT_DATE': 'period_ending'})

    return pivoted_cash_flow

def ak_stock_cash_flow(symbol: str,
                      limit: int = 10,
                      period: Literal["annual", "quarter"] = "quarter"
                      ) -> pd.DataFrame:
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    if market == "HK":
        return stock_hk_cash_flow(symbol, limit, period)
    else:
        import akshare as ak
        symbol_em = f"{market}{symbol_b}"

        if period == "annual":
            return ak.stock_cash_flow_sheet_by_yearly_em(symbol=symbol_em)
        elif period == "quarter":
            return ak.stock_cash_flow_sheet_by_report_em(symbol=symbol_em)
        else:
            raise ValueError("Invalid period. Please use 'annual' or 'quarter'.")
