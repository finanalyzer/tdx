import sqlite3
import pandas as pd
import time
import pickle
import logging
from mysharelib.tools import setup_logger
from openbb_akshare import project_name

setup_logger(project_name)

CACHE_TTL = 60*60  # 60 seconds
logger = logging.getLogger(__name__)

def get_connection():
    from mysharelib import get_cache_path
    db_path = get_cache_path(project_name)

    return sqlite3.connect(db_path)

def init_cache_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equity_quote (
                key TEXT PRIMARY KEY,
                timestamp REAL,
                data BLOB
            )
        ''')
        conn.commit()

def get_data(market):
    import akshare as ak

    if market == "HK":
        # Get Hong Kong stock market data
        df = ak.stock_hk_spot_em()
    elif market == "SH" or market == "SS":
        df = ak.stock_sh_a_spot_em()
    elif market == "SZ":
        df = ak.stock_sz_a_spot_em()
    elif market == "BJ":
        # Get Beijing stock market data
        df = ak.stock_bj_a_spot_em()
    else:
        # Get A-share market data
        df = pd.DataFrame()

    #return df[["代码", "名称", "最新价", "今开", "最高", "最低", "涨跌幅", "涨跌额", "成交量", "昨收"]]
    return df

def get_exchange_name(market):
    if market == "HK":
        return "HKEX"
    elif market == "SH" or market == "SS":
        return "SSE"
    elif market == "SZ":
        return "SZSE"
    elif market == "BJ":
        return "BSE"
    else:
        raise ValueError(f"Unsupported market: {market}")

def get_primary_key(market):
    if market == "HK":
        return "equity_quote_HK"
    elif market == "SH" or market == "SS":
        return "equity_quote_SH"
    elif market == "SZ":
        return "equity_quote_SZ"
    elif market == "BJ":
        return "equity_quote_BJ"
    else:
        raise ValueError(f"Unsupported market: {market}")

def load_cached_data(market, use_cache=True)->pd.DataFrame:
    if not use_cache:
        logger.info("Cache disabled, fetching fresh data...")
        return get_data(market)
    
    key=get_primary_key(market)
    init_cache_table()

    now = time.time()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, data FROM equity_quote WHERE key=?', (key,))
        row = cursor.fetchone()

        if row:
            timestamp, data_blob = row
            if now - timestamp < CACHE_TTL:
                logger.info("Loading from SQLite cache...")
                return pickle.loads(data_blob)

        logger.info("Generating new data...")
        df = get_data(market)

        # 序列化 DataFrame
        data_blob = pickle.dumps(df)

        # 更新或插入缓存
        cursor.execute('''
            INSERT OR REPLACE INTO equity_quote (key, timestamp, data)
            VALUES (?, ?, ?)
        ''', (key, now, data_blob))

        conn.commit()
        return df

if __name__ == "__main__":

    # 使用示例
    df = load_cached_data("SH")
    logger.info(df.head())

    # 等待超过 TTL 再次调用会刷新
    #time.sleep(65)
    df2 = load_cached_data("HK")
    logger.info(df2.head())