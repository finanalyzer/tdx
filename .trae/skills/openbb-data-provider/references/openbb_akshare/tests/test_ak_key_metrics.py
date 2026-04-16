import pytest
import pandas as pd
from openbb_akshare.utils.ak_key_metrics import fetch_key_metrics

def test_fetch_key_metrics_invalid_symbol(akshare_api_key):
    """Test fetch_key_metrics with invalid symbol returns empty DataFrame"""
    result = fetch_key_metrics("INVALID", api_key=akshare_api_key)
    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_fetch_key_metrics_periods():
    """Test fetch_key_metrics with different periods"""
    # Test quarter period
    df_quarter = fetch_key_metrics("601127.SH", period="quarter")
    assert isinstance(df_quarter, pd.DataFrame)
    
    # Test annual period
    df_annual = fetch_key_metrics("601127.SH", period="annual")
    assert isinstance(df_annual, pd.DataFrame)

def test_fetch_key_metrics_cache():
    """Test fetch_key_metrics caching behavior"""
    # Test with cache
    df_cached = fetch_key_metrics("601127.SH", use_cache=True)
    assert isinstance(df_cached, pd.DataFrame)
    
    # Test without cache
    df_no_cache = fetch_key_metrics("601127.SH", use_cache=False)
    assert isinstance(df_no_cache, pd.DataFrame)

def test_fetch_key_metrics_symbol_formats():
    """Test fetch_key_metrics with different symbol formats"""
    symbols = ["601127.SH", "601127"]
    for symbol in symbols:
        df = fetch_key_metrics(symbol)
        assert isinstance(df, pd.DataFrame)

@pytest.mark.parametrize("symbol", ["001979","600177","03988"])
def test_key_metrics(symbol, default_provider, logger):
    from openbb import obb
    df = obb.equity.fundamental.metrics(symbol=symbol, provider=default_provider, use_cache=True).to_dataframe()
    assert isinstance(df, pd.DataFrame)
    logger.info(df)
