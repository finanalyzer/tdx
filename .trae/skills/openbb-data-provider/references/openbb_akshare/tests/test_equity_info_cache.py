import pytest
import pandas as pd
import sqlite3
from pathlib import Path
import gc
import time
from datetime import datetime, timezone
from mysharelib.table_cache import TableCache
from openbb_akshare.utils.fetch_equity_info import EQUITY_INFO_SCHEMA
from openbb_akshare import project_name


def _safe_unlink(path: Path, attempts: int = 5, delay_s: float = 0.1) -> None:
    """Best-effort unlink for Windows where SQLite file locks can linger briefly."""
    for attempt in range(attempts):
        try:
            path.unlink()
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay_s)

@pytest.fixture
def sample_equity_info_df():
    def ts_to_date(ts):
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date() if ts else None

    data = {
        "symbol": ["601127"],  # 使用列表包裹以生成单行 DataFrame
        "org_name_en": ["Seres Group Co.,Ltd."],
        "main_operation_business": [
            "新能源汽车及核心三电(电池、电驱、电控)、传统汽车及核心部件总成的研发、制造、销售及服务。"
        ],
        "org_cn_introduction": [
            "赛力斯始创于1986年，是以新能源汽车为核心业务的技术科技型汽车企业。现有员工1.6万人，A..."
        ],
        "chairman": ["张正萍"],
        "org_website": ["www.seres.com.cn"],
        "reg_address_cn": ["重庆市沙坪坝区五云湖路7号"],
        "office_address_cn": ["重庆市沙坪坝区五云湖路7号"],
        "telephone": ["86-23-65179666"],
        "postcode": ["401335"],
        "provincial_name": ["重庆市"],
        "staff_num": [16102],
        "affiliate_industry": ["{'ind_code': 'BK0025', 'ind_name': '汽车整车'}"],
        "operating_scope": [
            "一般项目：制造、销售：汽车零部件、机动车辆零部件、普通机械、电器机械、电器、电子产品（不..."
        ],
        "listed_date": [ts_to_date(1465920000000)],
        "org_name_cn": ["赛力斯集团股份有限公司"],
        "org_short_name_cn": ["赛力斯"],
        "org_short_name_en": ["SERES"],
        "org_id": ["T000071215"],
        "established_date": [ts_to_date(1178812800000)],
        "actual_issue_vol": [142500000.0],
        "reg_asset": [1509782193.0],
        "issue_price": [5.81],
        "currency": ["CNY"]
    }

    df = pd.DataFrame(data)
    return df

@pytest.fixture
def test_db_path(tmp_path):
    return str(tmp_path / "test_equity.db")

@pytest.fixture
def equity_cache(test_db_path):
    cache = TableCache(EQUITY_INFO_SCHEMA, project=project_name, db_path=test_db_path, table_name="equity_info", primary_key="symbol")
    yield cache
    try:
        cache.close()
    except Exception:
        pass
    gc.collect()
    if Path(test_db_path).exists():
        _safe_unlink(Path(test_db_path))

def test_db_creation(test_db_path):
    cache = TableCache(EQUITY_INFO_SCHEMA, project=project_name, db_path=test_db_path, table_name="equity_info", primary_key="symbol")
    assert Path(test_db_path).exists()
    cache.close()

def test_write_and_read_dataframe(sample_equity_info_df, equity_cache):
    test_data = sample_equity_info_df
    
    equity_cache.write_dataframe(test_data)
    result = equity_cache.read_dataframe()
    
    for col in test_data.columns:
        if col == 'listed_date' or col == 'established_date':
            # Convert datetime to date for comparison
            if pd.api.types.is_datetime64_any_dtype(test_data[col]):
                test_data[col] = test_data[col].dt.date
                result[col] = result[col].dt.date
        else:
            pd.testing.assert_series_equal(
                test_data[col].reset_index(drop=True),
                result[col].reset_index(drop=True),
                check_names=False
            )

def test_update_or_insert(sample_equity_info_df, equity_cache):
    initial_data = sample_equity_info_df
    update_data = initial_data.copy()
    update_data['org_name_en'] = ['UpdatedCompany1']

    equity_cache.write_dataframe(initial_data)
    equity_cache.update_or_insert(update_data)

    result = equity_cache.read_dataframe()
    assert result.loc[0, 'org_name_en'] == 'UpdatedCompany1'

def test_connection_management(equity_cache):
    equity_cache.connect()
    assert isinstance(equity_cache.conn, sqlite3.Connection)
    
    equity_cache.close()
    with pytest.raises(AttributeError):
        equity_cache.conn.cursor()

@pytest.mark.parametrize("symbol", ["02800", "00011", "600177"])

def test_ak_xq_fetch_equity_info(symbol, logger):
    """
    Test akshare equity info. 
    - 02800 returns nan for listed date.
    - 00011 returns 1952-12-04 for established_date.
    """
    from openbb import obb
    equity_info_df = obb.equity.profile(symbol=symbol, provider="akshare").to_dataframe()
    logger.info(f"obb.equity.profile:{symbol}, {len(equity_info_df)}")
    assert equity_info_df.shape[0] > 0
