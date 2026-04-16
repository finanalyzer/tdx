import pytest
from openbb import obb
import pandas as pd

@pytest.mark.parametrize("symbol", ["001979"])
@pytest.mark.parametrize("use_cache", [True, False])

def test_equity_cn_news(symbol, use_cache):
    df = obb.news.company(
        symbol=symbol, provider="akshare", use_cache=use_cache
    ).to_dataframe()
    assert isinstance(df, pd.DataFrame)