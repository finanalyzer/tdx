import json
import pandas as pd
import akshare as ak
import logging
from mysharelib.tools import setup_logger
from openbb_akshare import project_name

setup_logger(project_name)

logger = logging.getLogger(__name__)

EQUITY_INFO_SCHEMA = {
    "symbol": "TEXT PRIMARY KEY",
    "org_name_en": "TEXT",
    "main_operation_business": "TEXT",
    "org_cn_introduction": "TEXT",
    "chairman": "TEXT",
    "org_website": "TEXT",
    "reg_address_cn": "TEXT",
    "office_address_cn": "TEXT",
    "telephone": "TEXT",
    "postcode": "TEXT",
    "provincial_name": "TEXT",
    "staff_num": "INTEGER",
    "affiliate_industry": "TEXT",
    "operating_scope": "TEXT",
    "listed_date": "DATE",
    "org_name_cn": "TEXT",
    "org_short_name_cn": "TEXT",
    "org_short_name_en": "TEXT",
    "org_id": "TEXT",
    "established_date": "DATE",
    "actual_issue_vol": "INTEGER",
    "reg_asset": "REAL",
    "issue_price": "REAL",
    "currency": "TEXT"
}

def serialize_dict_fields(d):
    return {k: json.dumps(v) if isinstance(v, dict) else v for k, v in d.items()}

def fetch_equity_info(symbol: str, api_key: str | None = None, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetches detailed information about a specific equity symbol.

    Args:
        symbol (str): The stock symbol to fetch information for.
                      such as "601127.SH".

    Returns:
        dict: A dictionary containing the equity information.
    """
    from mysharelib.table_cache import TableCache
    from mysharelib.tools import normalize_symbol

    symbol_b, symbol_f, market = normalize_symbol(symbol)
    cache = TableCache(EQUITY_INFO_SCHEMA, project=project_name, table_name="equity_info", primary_key="symbol")

    if use_cache:
        data = cache.read_dataframe()
        result = data[data["symbol"] == symbol_f]
        if not result.empty:
            #logger.info(f"Using cached equity info for symbol: {symbol_f}")
            return result

    columns = list(EQUITY_INFO_SCHEMA.keys())
    equity_info = pd.DataFrame(columns=columns)
    try:
        if api_key:
            ak.stock.cons.xq_a_token = api_key
        if market == "HK":
            stock_individual_basic_info_hk_xq_df = ak.stock_individual_basic_info_hk_xq(symbol=symbol_b)
            hk_data = stock_individual_basic_info_hk_xq_df.set_index("item").T
            row = {}
            row["symbol"] = symbol_f
            row["org_name_en"] = hk_data["comenname"].iloc[0]
            row["main_operation_business"] = hk_data["mbu"].iloc[0]
            row["org_cn_introduction"] = hk_data["comintr"].iloc[0]
            row["chairman"] = hk_data["chairman"].iloc[0]
            row["org_website"] = hk_data["web_site"].iloc[0]
            row["reg_address_cn"] = hk_data["rgiofc"].iloc[0]
            row["office_address_cn"] = hk_data["hofclctmbu"].iloc[0]
            row["telephone"] = hk_data["tel"].iloc[0]
            row["postcode"] = ""
            row["provincial_name"] = ""
            row["staff_num"] = 0
            row["affiliate_industry"] = ""
            row["operating_scope"] = hk_data["refccomty"].iloc[0]
            row["listed_date"] = hk_data["lsdateipo"].iloc[0]
            row["org_name_cn"] = hk_data["comcnname"].iloc[0]
            row["org_short_name_cn"] = ""
            row["org_short_name_en"] = ""
            row["org_id"] = hk_data["comunic"].iloc[0]
            row["established_date"] = hk_data["incdate"].iloc[0]
            row["actual_issue_vol"] = hk_data["numtissh"].iloc[0]
            row["reg_asset"] = 0.0
            row["issue_price"] = hk_data["ispr"].iloc[0]
            row["currency"] = "HKD"
            equity_info.loc[len(equity_info)] = row
            cache.update_or_insert(equity_info)
        else:
            stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol=f"{market}{symbol_b}")
            keys = list(EQUITY_INFO_SCHEMA.keys())
            equity_info=stock_individual_basic_info_xq_df.set_index("item").T[keys[1:]]

            serialized_data = [serialize_dict_fields(item) for item in equity_info.to_dict(orient="records")]
            df = pd.DataFrame([{"symbol": symbol_f, **serialized_data[0]}])
            cache.update_or_insert(df)
    except Exception as e:
        print(f"Error fetching equity info for {symbol}: {e}")
        return pd.DataFrame(columns=columns)

    data = cache.read_dataframe()
    result = data[data["symbol"] == symbol_f]
    result["listed_date"] = pd.to_datetime(result["listed_date"], unit='ms')
    result["established_date"] = pd.to_datetime(result["established_date"], unit='ms')
    # logger.info(f"Fetched equity info for symbol: {symbol_f}")

    return result
