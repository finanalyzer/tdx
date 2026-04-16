import logging
import pandas as pd
from mysharelib.tools import setup_logger, get_exchange
from mysharelib.table_cache import TableCache
from openbb_akshare import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)

TABLE_SCHEMA = {
    "symbol": "TEXT",               # Symbol (e.g. 600000)
    "name": "TEXT",                 # Short name of the asset
    "exchange": "TEXT"              # Exchange code (e.g. SSE/SZSE)
}

def get_symbols_df() -> pd.DataFrame:
    import akshare as ak

    stock_info_a_code_name_df = ak.stock_info_a_code_name()
    stock_info_a_code_name_df.rename(columns={"code": "symbol"}, inplace=True)
    stock_info_a_code_name_df['exchange'] = [
        get_exchange(code)
        for code in stock_info_a_code_name_df['symbol']
        ]
    # Get symbols for HK market
    hk_stock_list_df = ak.stock_hk_spot_em()
    stock_info_hk_code_name_df = hk_stock_list_df[["代码","名称"]].copy()
    stock_info_hk_code_name_df.rename(columns={"代码": "symbol", "名称": "name"}, inplace=True)
    stock_info_hk_code_name_df["exchange"] = "HKEX"
    
    return pd.concat([stock_info_a_code_name_df, stock_info_hk_code_name_df], ignore_index=True) 

def get_symbols(use_cache: bool = True, api_key : str = "") -> pd.DataFrame:
    cache = TableCache(TABLE_SCHEMA, project=project_name, table_name="symbols", primary_key="symbol")
    if use_cache:
        data = cache.read_dataframe()
        if not data.empty:
            logger.info(f"Loading symbols from {project_name} cache...")
            return data

    logger.info(f"Generating symbols for {project_name} ...")
    data = get_symbols_df()
    cache.write_dataframe(data)
    return data