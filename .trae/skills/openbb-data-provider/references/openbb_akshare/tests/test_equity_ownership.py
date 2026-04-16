import pytest
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from mysharelib.table_cache import TableCache
from openbb_akshare.utils.fetch_equity_info import EQUITY_INFO_SCHEMA
from openbb_akshare import project_name

@pytest.mark.parametrize("symbol", ["00386", "600177"])

def test_ak_equity_ownership(symbol, logger):
    from openbb_akshare.utils.ak_equity_ownership import stock_gdfx_top_10
    equity_owners_df = stock_gdfx_top_10(symbol, date="20250630")
    logger.info(f"obb.equity.ownership:{symbol}, {equity_owners_df}")

