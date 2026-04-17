"""Test TdxQuant Equity Quote Model."""

import pytest
from openbb_tdx.models.equity_quote import (
    TdxQuantEquityQuoteQueryParams,
    TdxQuantEquityQuoteData,
    TdxQuantEquityQuoteFetcher,
)


def test_tdxquant_equity_quote_query_params():
    """Test TdxQuantEquityQuoteQueryParams."""
    # Test with valid parameters
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ")
    assert params.symbol == "000001.SZ"
    assert params.use_cache is True

    # Test with multiple symbols
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ,000002.SZ")
    assert params.symbol == "000001.SZ,000002.SZ"

    # Test with use_cache=False
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ", use_cache=False)
    assert params.use_cache is False


def test_tdxquant_equity_quote_data():
    """Test TdxQuantEquityQuoteData."""
    # Test with valid data
    data = {
        "code": "000001.SZ",
        "name": "平安银行",
        "price": 15.23,
        "open": 15.10,
        "high": 15.30,
        "low": 15.05,
        "prev_close": 15.00,
        "volume": 10000000,
        "change": 0.23,
        "change_pct": 1.53,
        "year_high": 18.00,
        "year_low": 12.00,
        "bid": 15.22,
        "bid_volume": 1000,
        "ask": 15.24,
        "ask_volume": 1000,
        "exchange": "SZ",
        "market_center": "TdxQuant",
        "last_volume": 100,
        "close": 15.23,
        "exchange_volume": 10000000,
    }
    quote_data = TdxQuantEquityQuoteData(**data)
    assert quote_data.symbol == "000001.SZ"
    assert quote_data.name == "平安银行"
    assert quote_data.last_price == 15.23
    assert quote_data.open == 15.10
    assert quote_data.high == 15.30
    assert quote_data.low == 15.05
    assert quote_data.prev_close == 15.00
    assert quote_data.volume == 10000000
    assert quote_data.change == 0.23
    assert quote_data.change_percent == 1.53
    assert quote_data.year_high == 18.00
    assert quote_data.year_low == 12.00


def test_tdxquant_equity_quote_fetcher_transform_query():
    """Test TdxQuantEquityQuoteFetcher.transform_query."""
    params = {"symbol": "000001.SZ"}
    transformed_params = TdxQuantEquityQuoteFetcher.transform_query(params)
    assert isinstance(transformed_params, TdxQuantEquityQuoteQueryParams)
    assert transformed_params.symbol == "000001.SZ"


def test_tdxquant_equity_quote_fetcher_extract_data():
    """Test TdxQuantEquityQuoteFetcher.extract_data."""
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ")
    credentials = {"tdxquant_api_key": "test_api_key"}
    data = TdxQuantEquityQuoteFetcher.extract_data(params, credentials)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "symbol" in data[0]
    assert "name" in data[0]
    assert "last_price" in data[0]


def test_tdxquant_equity_quote_fetcher_transform_data():
    """Test TdxQuantEquityQuoteFetcher.transform_data."""
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ")
    test_data = [
        {
            "code": "000001.SZ",
            "name": "平安银行",
            "price": 15.23,
            "open": 15.10,
            "high": 15.30,
            "low": 15.05,
            "prev_close": 15.00,
            "volume": 10000000,
            "change": 0.23,
            "change_pct": 1.53,
            "year_high": 18.00,
            "year_low": 12.00,
        }
    ]
    transformed_data = TdxQuantEquityQuoteFetcher.transform_data(params, test_data)
    assert isinstance(transformed_data, list)
    assert len(transformed_data) > 0
    assert isinstance(transformed_data[0], TdxQuantEquityQuoteData)


def test_tdxquant_equity_quote_fetcher_with_invalid_symbol():
    """Test TdxQuantEquityQuoteFetcher with invalid symbol."""
    params = TdxQuantEquityQuoteQueryParams(symbol="INVALID.SZ")
    credentials = None
    data = TdxQuantEquityQuoteFetcher.extract_data(params, credentials)
    assert isinstance(data, list)
    # Invalid symbol should return empty list or list with error
    assert len(data) == 0 or (len(data) > 0 and "error" in data[0])


def test_tdxquant_equity_quote_fetcher_with_multiple_symbols():
    """Test TdxQuantEquityQuoteFetcher with multiple symbols."""
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ,000002.SZ")
    credentials = {"tdxquant_api_key": "test_api_key"}
    data = TdxQuantEquityQuoteFetcher.extract_data(params, credentials)
    assert isinstance(data, list)
    assert len(data) >= 2
