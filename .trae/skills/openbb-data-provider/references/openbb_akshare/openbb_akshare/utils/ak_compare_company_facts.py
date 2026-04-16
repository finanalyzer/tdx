import logging
import pandas as pd
from typing import Optional, Literal
from openbb_akshare import project_name
from mysharelib.tools import setup_logger, normalize_symbol

setup_logger(project_name)
logger = logging.getLogger(__name__)

def fetch_compare_company(
        symbol: str, 
        period: Literal["annual", "quarter"] = "quarter",
        use_cache: bool = True,
        api_key : Optional[str] = ""
        ) -> pd.DataFrame:
    """
    Fetches financial metrics for a specific equity symbol.

    Args:
        symbol (str): The stock symbol to fetch metrics for.
                      such as "601127.SH".

    Returns:
        pd.DataFrame: A DataFrame containing the metrics.
    """
    from mysharelib.blob_cache import BlobCache

    symbol_b, _, market = normalize_symbol(symbol)
    if market not in ["SH", "SZ", "BJ", "HK"]:
        logger.warning("fetch_compare_company只支持A股和港股。")
        return pd.DataFrame()
    cache = BlobCache(table_name="compare_company_facts", project=project_name)
    data = cache.load_cached_data(symbol_b, period, use_cache, _get_metrics, api_key=api_key)
    if data is None:
        return pd.DataFrame()
    else:
        return data
def _get_metrics(
    symbol: str,
    period: str = "quarter",
    api_key : Optional[str] = ""
) -> pd.DataFrame:
    from mysharelib.em.get_a_info_em import get_a_info_em
    from mysharelib.em.get_hk_info_em import get_hk_info_em

    _, symbol_f, market = normalize_symbol(symbol)
    if market in ["HK"]:
        _, df_comparison = get_hk_info_em(symbol_f)
    else:
        _, df_comparison = get_a_info_em(symbol_f)

    return df_comparison
