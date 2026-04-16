from datetime import (
    date as dateType,
    datetime,
)
import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger, normalize_symbol
from mysharelib.em.stock_hk_gdfx_em import stock_hk_gdfx_top_10_em

setup_logger(project_name)
logger = logging.getLogger(__name__)

def stock_gdfx_top_10(symbol:str, date: dateType | str):
    import akshare as ak

    if isinstance(date, str):
        # Assuming date format is 'YYYYMMDD'
        try:
            # Try parsing as 'YYYY-MM-DD'
            date = datetime.strptime(date, "%Y%m%d")
        except ValueError:
            try:
                # Try parsing as 'YYYY-MM-DD'
                date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use 'YYYY-MM-DD' or 'YYYYMMDD'.")
    
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    if market == "HK":
        return stock_hk_gdfx_top_10_em(symbol=symbol_f, date=date.strftime("%Y%m%d"))
    elif market in ["SH", "SZ", "BJ"]:
        return ak.stock_gdfx_free_top_10_em(symbol=f"sh{symbol_b}", date=date.strftime("%Y%m%d"))
    else:
        raise ValueError("Invalid market. Please use 'HK', 'SH', 'SZ', or 'BJ'.")