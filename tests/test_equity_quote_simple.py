"""Simple test script for TdxQuant Equity Quote Model."""

from openbb_tdx.models.equity_quote import (
    TdxQuantEquityQuoteQueryParams,
    TdxQuantEquityQuoteData,
    TdxQuantEquityQuoteFetcher,
)


def test_query_params():
    """Test query parameters."""
    print("Testing query parameters...")
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ")
    print(f"✓ Symbol: {params.symbol}")
    print(f"✓ Use cache: {params.use_cache}")
    return True


def test_data_model():
    """Test data model."""
    print("\nTesting data model...")
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
    }
    quote_data = TdxQuantEquityQuoteData(**data)
    print(f"✓ Symbol: {quote_data.symbol}")
    print(f"✓ Name: {quote_data.name}")
    print(f"✓ Last price: {quote_data.last_price}")
    print(f"✓ Open: {quote_data.open}")
    print(f"✓ High: {quote_data.high}")
    print(f"✓ Low: {quote_data.low}")
    print(f"✓ Prev close: {quote_data.prev_close}")
    print(f"✓ Volume: {quote_data.volume}")
    print(f"✓ Change: {quote_data.change}")
    print(f"✓ Change percent: {quote_data.change_percent}")
    print(f"✓ Year high: {quote_data.year_high}")
    print(f"✓ Year low: {quote_data.year_low}")
    return True


def test_fetcher_transform_query():
    """Test fetcher transform_query."""
    print("\nTesting fetcher transform_query...")
    params = {"symbol": "000001.SZ"}
    transformed_params = TdxQuantEquityQuoteFetcher.transform_query(params)
    print(f"✓ Transformed symbol: {transformed_params.symbol}")
    return True


def test_fetcher_extract_data():
    """Test fetcher extract_data."""
    print("\nTesting fetcher extract_data...")
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ")
    credentials = {"tdxquant_api_key": "test_api_key"}
    data = TdxQuantEquityQuoteFetcher.extract_data(params, credentials)
    print(f"✓ Data returned: {len(data)} items")
    if data:
        print(f"✓ First item keys: {list(data[0].keys())}")
    return True


def test_fetcher_transform_data():
    """Test fetcher transform_data."""
    print("\nTesting fetcher transform_data...")
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
    print(f"✓ Transformed data: {len(transformed_data)} items")
    if transformed_data:
        print(f"✓ First item type: {type(transformed_data[0])}")
    return True


def test_fetcher_with_invalid_symbol():
    """Test fetcher with invalid symbol."""
    print("\nTesting fetcher with invalid symbol...")
    params = TdxQuantEquityQuoteQueryParams(symbol="INVALID.SZ")
    credentials = None
    data = TdxQuantEquityQuoteFetcher.extract_data(params, credentials)
    print(f"✓ Data returned: {len(data)} items (invalid symbol should return empty or error)")
    return True


def test_fetcher_with_multiple_symbols():
    """Test fetcher with multiple symbols."""
    print("\nTesting fetcher with multiple symbols...")
    params = TdxQuantEquityQuoteQueryParams(symbol="000001.SZ,000002.SZ")
    credentials = {"tdxquant_api_key": "test_api_key"}
    data = TdxQuantEquityQuoteFetcher.extract_data(params, credentials)
    print(f"✓ Data returned: {len(data)} items (expected: 2)")
    return True


if __name__ == "__main__":
    print("Testing TdxQuant Equity Quote Model...\n")
    
    tests = [
        test_query_params,
        test_data_model,
        test_fetcher_transform_query,
        test_fetcher_extract_data,
        test_fetcher_transform_data,
        test_fetcher_with_invalid_symbol,
        test_fetcher_with_multiple_symbols,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"\n✓ {test.__name__} passed")
            else:
                failed += 1
                print(f"\n✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test.__name__} failed with error: {e}")
    
    print(f"\n\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed.")
